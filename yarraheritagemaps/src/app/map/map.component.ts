/**
 * Copyright 2018 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {
  Component, ElementRef,
  Input, Output, EventEmitter,
  ViewChild, AfterViewInit,
  ComponentRef, Injector, ApplicationRef, ComponentFactoryResolver, NgZone } from '@angular/core';

import { StyleProps, StylesService, LayerStyles } from '../services/styles.service';
import * as parseWKT from 'wellknown';
import { OverlayProperties } from '../main/panels/overlays-properties';
import { AppSettings } from '../services/appsettings.service';

declare var geoXML3: any;
import '../../../third_party/geocodezip/geoxml3.js';
import { style } from '@angular/animations';
import { OverlayInfoComponent as OverlayInfoComponent } from '../main/panels/overlay-info/overlay-info.component';

import { SelectMMBWOverlay } from '../services/select-MMBWOverlay';
import { GCS_BUCKET_SOS, HERITAGE_SITE_ZINDEX, HERITAGE_OVERLAY_STYLE } from '../app.constants';
import { HeritageSiteInfo } from '../main/panels/heritage-site-info/heritage-site-info';
import { HeritageSiteInfoComponent } from '../main/panels/heritage-site-info/heritage-site-info.component';
import { LayerDescription } from '../services/layers-info-service';
import { Subject } from 'rxjs';

interface IFeature {
  setMap(map: google.maps.Map|null): void;
  setOptions(options: google.maps.PolylineOptions|google.maps.PolygonOptions): void;
  addListener(type: string, fn: (e: google.maps.MouseEvent) => void): void;
}

@Component({
  selector: 'app-map',
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.css']
})
export class MapComponent implements AfterViewInit {
  // DOM element for map.
  @ViewChild('mapEl',  {static: true}) mapEl: ElementRef;
  @ViewChild('mouseinfo',  {static: true}) mouseinfo: ElementRef;

  // Maps API instance.
  map: google.maps.Map;

  // Info window for display over Maps API.
  infoWindow: google.maps.InfoWindow = null;
  overlayInfoComponentRef: ComponentRef<OverlayInfoComponent>;
  heritageSiteInfoComponentRef: ComponentRef<HeritageSiteInfoComponent>;
  // Basemap styles.
  pendingStyles: Promise<Array<google.maps.MapTypeStyle>>;

  // Styling service.
  readonly styler = new StylesService();

  private _rows: Array<Object>;
  private _overlay_rows: Array<Object>;
  private _geoColumn = 'bndry';
  private _overlaysLayer: google.maps.Data;
  private _propertiesLayer: google.maps.Data;
  private _planningLayer: google.maps.Data;
  private _mmbwOverlay: Array<Object>;
  private _geoXml: any = null;
  mapheight = '{height:"40px"}';

  @Output() overlayChanged: EventEmitter<OverlayProperties> =   new EventEmitter();
  @Output() overlaySelected: EventEmitter<OverlayProperties> =   new EventEmitter();
  private highlightedOverlay: OverlayProperties = new OverlayProperties(null);
  private seletedOverlay: OverlayProperties = new OverlayProperties(null);

  @Output() heritageSiteChanged: EventEmitter<HeritageSiteInfo> =   new EventEmitter();
  @Output() heritgeSiteSelected: EventEmitter<HeritageSiteInfo> =   new EventEmitter();
  private highlightedHeritageSiteInfo: HeritageSiteInfo = new HeritageSiteInfo(null);
  private selectedHeritageSiteInfo: HeritageSiteInfo = new HeritageSiteInfo(null);

  @Input()
  set rows(rows: Array<Object>) {
    if (rows.length) {
      this._rows = rows;
      this.updateGeoJSON();
    }
  }

  @Input()
  set geoColumn(geoColumn: string) {
    const tmp = this._geoColumn;
    if (geoColumn) {
      this._geoColumn = geoColumn;
      if (geoColumn !== tmp) {
        this.updateGeoJSON();
      }
    }
  }

  @Input()
  set styles(styles: LayerStyles) {
    this.updateStyles(styles);
  }

  @Input()
  set selectedLayersInfo(layerInfo: Array<LayerDescription>) {
    this.updateSelectedLayersInfo(layerInfo);
  }

  @Input()
  set mmbwOverlay(mmbwOverlay: Array<SelectMMBWOverlay>) {
    this._mmbwOverlay = mmbwOverlay;
    if (this._geoXml !== null) {
      this._geoXml.hideDocument();
    }
    if (this._mmbwOverlay  != null) {
      this._mmbwOverlay.forEach( (m: SelectMMBWOverlay) => {
        this.handleMMBWSelected(m);
      });
    }
  }

  @Input()
  hidePropertySubject: Subject<any>;


  constructor (
    private injector: Injector,
    private resolver: ComponentFactoryResolver,
    private appRef: ApplicationRef,
    private zone: NgZone
    ) {
    this.pendingStyles = fetch('assets/basemap.json', {credentials: 'include'})
      .then((response) => response.json());
  }

  /**
   * Constructs a Maps API instance after DOM has initialized.
   */
  ngAfterViewInit() {

    this.mapEl.nativeElement.style.height = '100' + '%';

    Promise.all([ pendingMap, this.pendingStyles ])
      .then(([_, mapStyles]) => {
          const appSettings: AppSettings = new AppSettings(); // get copy of current values
          const mapCenter: google.maps.LatLng = appSettings.mapCenter;
          const mapZoom: number = appSettings.mapZoom;
          const mapOptions =  {
          center: mapCenter,
          zoom: mapZoom,
          mapTypeControl: true, // hide the Map and Satellite options
          zoomControl: true,
          zoomControlOptions: {
              position: google.maps.ControlPosition.TOP_RIGHT
          },
          scaleControl: true,
          streetViewControl: true,
          streetViewControlOptions: {
              position: google.maps.ControlPosition.TOP_RIGHT
          }
        };
        this.map = new google.maps.Map(this.mapEl.nativeElement, mapOptions);
        this.map.setOptions({styles: mapStyles});
        this._overlaysLayer = new google.maps.Data();
        this._propertiesLayer = new google.maps.Data();
        this._planningLayer = new google.maps.Data();

        this.map.addListener('click', (event: google.maps.MouseEvent) => {
            console.log(`click lat:${event.latLng.lat}, lng:${event.latLng.lng}`);
        });

        this.hidePropertySubject.subscribe(event => {
          if (event !== null) {
            this.removeMatchingFeaturesFromLayer(this._propertiesLayer, 'row_num', event.row_num);
            console.log('Heritage Site Removed from Map', event);
          }
        });
      });
  }

  findFeatureRow(row_num: Number) {
    return this.rows.find(row => row['row_num'] === row_num);
  }


  islayerSelected(layerInfo: Array<LayerDescription>, name: string): boolean {
    return layerInfo.find((layer) => {
      return layer.name === name;
    }) ? true : false;
  }

  updateSelectedLayersInfo(layerInfo: Array<LayerDescription>) {

    if (this._overlaysLayer) {
      this._overlaysLayer.setMap(this.islayerSelected(layerInfo, 'Overlays') ?
      this.map :
      null);
    }
    if (this._propertiesLayer) {
      this._propertiesLayer.setMap(this.islayerSelected(layerInfo, 'Sites') ?
      this.map :
      null);
    }
    if (this._planningLayer) {
      this._planningLayer.setMap(this.islayerSelected(layerInfo, 'Planning') ?
      this.map :
      null);
    }
    // this._mmbwOverlay.setMap(this.islayerSelected('Heritage Maps') ? this.map : null);
  }

  handleMMBWSelected(mmbwOvl: SelectMMBWOverlay) {
    if (mmbwOvl !== null) {
      this.infoWindow = new google.maps.InfoWindow({
        content: 'MMBW Map'});

      this._geoXml = new geoXML3.parser({
        map: this.map,
        infoWindow: this.infoWindow,
        singleInfoWindow: true,
      });
      const kml = mmbwOvl.KMLurl;
      this._geoXml.parse(kml);
    }
  }

  removeFeaturesFromLayer(layer): boolean {
    layer.forEach((feature) => {
      if (Array.isArray(feature)) {
        feature.forEach((f) => {
          layer.remove(f);
          return true;
        });
      } else {
        layer.remove(feature);
        return true;
      }
    });
    return false;
  }

  removeMatchingFeaturesFromLayer(layer, key, value) {
    layer.forEach((feature) => {
      if (Array.isArray(feature)) {
        feature.forEach((f) => {
          if (f.getProperty(key) === value) {
            layer.remove(f);
          }
        });
      } else {
        if (feature.getProperty(key) === value) {
          layer.remove(feature);
        }
      }
    });
  }

  /* private utility is only called by this.hideOnlyMatchingFeaturesFromLayer() */
  private _overrideStyleOnFeature(feature, layer, key, value,  overrideStyle, defaultStyle) {
    if (feature.getProperty(key) === value) {
      if (this.map) {
        layer.overrideStyle(feature, overrideStyle);
      }
    } else {
      if (this.map) {
        layer.overrideStyle(feature, defaultStyle);
      }
    }
  }

  /* Apply an overrideStyle style to features in a data layer that  match key==value
   * All non-matching features will have the default style applied.
   * Otherwise all features except the matching feature is hidden!
   * Examples:
   *    overrideStyle = { clickable: false,strokeWeight: 3}
   *    defaultStyle = { clickable: true,strokeWeight: 1}
   */

  overrideStyleOnMatchingFeaturesInLayer(layer, key, value, overrideStyle, defaultStyle) {
    layer.forEach((feature) => {
      if (Array.isArray(feature)) {
        feature.forEach((f) => {
          this._overrideStyleOnFeature(f, layer, key, value, overrideStyle, defaultStyle);
        });
      } else {
        this._overrideStyleOnFeature(feature, layer, key, value, overrideStyle, defaultStyle);
      }
    });
  }

  removeMismatchingFeaturesFromLayer(layer, key, value) {
    layer.forEach((feature) => {
      if (Array.isArray(feature)) {
        feature.forEach((f) => {
          if (f.getProperty(key) !== value) {
            layer.remove(f);
          }
        });
      } else {
        if (feature.getProperty(key) !== value) {
          layer.remove(feature);
        }
      }
    });
  }
  backgroundMatchingFeaturesFromLayer(layer, key, value) {
    layer.forEach((feature) => {
      if (Array.isArray(feature)) {
        feature.forEach((f) => {
          if (f.getProperty(key) === value) {
            layer.remove(f);
            // layer.overrideStyle(f, {zIndex: 0});
          }
        });
      } else {
        if (feature.getProperty(key) === value) {
          layer.remove(feature);
          // layer.overrideStyle(feature, {zIndex: 0});
        }
      }
    });
  }

  addResultsToLayer(layer, rows, zIndex) {
    console.time(`Adding ${rows.length} Features`);
    try {
      rows.forEach((row) => {
        const g = row[this._geoColumn];
        const geometry = parseWKT(row[this._geoColumn]);
        const feature = {
          type: 'Feature',
          geometry,
          properties: row};
        layer.addGeoJson(feature);
        layer.overrideStyle(feature, {
                    zIndex: geometry.type === 'Point' ? zIndex + 1 : zIndex // point on top of polygons
        });
      });
    } catch (e) {
      // Parsing can fail (e.g. invalid WKT); just stop and log the error.
      console.error(e);
    }

    layer.setMap(this.map);
    console.timeEnd(`Adding ${rows.length} Features`);
  }

  /**
   * Converts row objects into GeoJSON, then loads into Maps API.
   */
  updateGeoJSON() {
    const map = this.map;
    if (!this._rows || !this._geoColumn) { return; }
    if (!map) {
      return;
    }
    const bounds = new google.maps.LatLngBounds(); // = map.getBounds();

    const isZonelayer =  ('ZONE_DESC' in this._rows[0]) ? true : false;
    const isPlanningLayer =  ('Estimated_Cost' in this._rows[0]) ? true : false;

    if (isZonelayer) {
      // Update the Overlays Key Map
      this._overlay_rows = this._rows;
      this._overlaysLayer.addListener('mouseover', (event) => {

          this.highlightedOverlay = new OverlayProperties(event);
          if (this.highlightedOverlay !== null) {
            this.overlayChanged.emit(this.highlightedOverlay);
          }
          this._overlaysLayer.overrideStyle(event.feature, {strokeWeight: 3});
      });

      this._overlaysLayer.addListener('mouseout', (event: google.maps.Data.MouseEvent) => {
        if (event.feature) {
          this.highlightedOverlay = null; // event.feature.getProperty('Overlay');
          this.overlayChanged.emit(this.highlightedOverlay);
          this._overlaysLayer.overrideStyle(event.feature, {strokeWeight: 1});
        }
      });

      this._overlaysLayer.addListener('click', (event: google.maps.Data.MouseEvent) => {
        if (event.feature) {
          this.highlightedOverlay = new OverlayProperties(event);
          this.overlayChanged.emit(this.highlightedOverlay );
          this.seletedOverlay = this.highlightedOverlay;
          this.overlaySelected.emit(this.seletedOverlay);
          this.zone.run(() => this.onMarkerClick(this._overlaysLayer, event));
        }
      });
      const appSettings: AppSettings = new AppSettings(); // get copy of current values
      if (appSettings.loadSitesForPreviousOverlay === false) {
        // no need to do zoom to this unless a new detail map layer is not about to be loaded.
        this._overlaysLayer.addListener('addfeature', function(e) {
          recursiveExtendBounds(e.feature.getGeometry(), bounds.extend, bounds);
          if (!bounds.isEmpty()) {
            map.fitBounds(bounds);
          }
        });
      }
      this.addResultsToLayer(this._overlaysLayer, this._rows, HERITAGE_OVERLAY_STYLE.zIndex);

      if (appSettings.loadSitesForPreviousOverlay === false || appSettings.previousSelectedOverlay === '') {
        appSettings.mapCenter = this.map.getCenter();
        appSettings.mapZoom = this.map.getZoom();
      }
    } else if (isPlanningLayer) {
      this.removeFeaturesFromLayer(this._planningLayer); // remove property details from last render.
      this._planningLayer.setMap(null);

      if (this.seletedOverlay.Overlay === '') {
        this.seletedOverlay.Overlay = this._rows[0]['Overlay'];
      }

      this._planningLayer.addListener('addfeature', function(e) {
        recursiveExtendBounds(e.feature.getGeometry(), bounds.extend, bounds);
        if (!bounds.isEmpty()) {
          map.fitBounds(bounds);
        }
      });
      this.addResultsToLayer(this._planningLayer, this._rows, HERITAGE_SITE_ZINDEX + 1);

      this._planningLayer.addListener('mouseover', (event: google.maps.Data.MouseEvent) => {

        this.highlightedHeritageSiteInfo = new HeritageSiteInfo(event);
        this.heritageSiteChanged.emit(this.highlightedHeritageSiteInfo);

        if (event.feature) {
          this._planningLayer.overrideStyle(event.feature, {
            strokeWeight: 3,
            zIndex: HERITAGE_SITE_ZINDEX
          });
        }
      });

      this._planningLayer.addListener('mouseout', (event: google.maps.Data.MouseEvent) => {
        if (event.feature) {
          this._planningLayer.overrideStyle(event.feature, {
              strokeWeight: 1,
              zIndex: HERITAGE_SITE_ZINDEX + 100
            });
        }
      });

      this._planningLayer.addListener('click', (event: google.maps.Data.MouseEvent) => {
        this.selectedHeritageSiteInfo = new HeritageSiteInfo(event);
        this.heritgeSiteSelected.emit(this.selectedHeritageSiteInfo);
        const feature = event ? event.feature : null;
        if (feature) {
          // this.showInfoWindow(e, e.latLng);
          this.zone.run(() => this.onMarkerClick(this._planningLayer, event));
        }
      });

    } else {  // Heritage Properties layer

      this.removeFeaturesFromLayer(this._propertiesLayer); // remove property details from last render.
      this._propertiesLayer.setMap(null);
      // const bounds = new google.maps.LatLngBounds();
      if (this.seletedOverlay.Overlay === '') {
        this.seletedOverlay.Overlay = this._rows[0]['Overlay'];
      }

      this.overrideStyleOnMatchingFeaturesInLayer(
              this._overlaysLayer,
              'Overlay',
              this.seletedOverlay.Overlay,
              { clickable: false, strokeWeight: 3},
              { clickable: true, strokeWeight: 1}
      );

      this._propertiesLayer.addListener('addfeature', function(e) {
        recursiveExtendBounds(e.feature.getGeometry(), bounds.extend, bounds);
        if (!bounds.isEmpty()) {
          map.fitBounds(bounds);
        }
      });
      this.addResultsToLayer(this._propertiesLayer, this._rows, HERITAGE_SITE_ZINDEX);
      const appSettings: AppSettings = new AppSettings(); // get copy of current values
      appSettings.mapCenter = this.map.getCenter();
      appSettings.mapZoom = this.map.getZoom();

      this._propertiesLayer.addListener('mouseover', (event: google.maps.Data.MouseEvent) => {

        this.highlightedHeritageSiteInfo = new HeritageSiteInfo(event);
        this.heritageSiteChanged.emit(this.highlightedHeritageSiteInfo);

        if (event.feature) {
          // console.log(this.highlightedHeritageSiteInfo.OriginalAddress);
          this._propertiesLayer.overrideStyle(event.feature, {
            strokeWeight: 3,
            zIndex: HERITAGE_SITE_ZINDEX
          });
        } else {
         //  console.log('mouse over no feautre');
        }
      });

      this._propertiesLayer.addListener('mouseout', (event: google.maps.Data.MouseEvent) => {
        if (event.feature) {
          this._propertiesLayer.overrideStyle(event.feature, {
              strokeWeight: 1,
              zIndex: HERITAGE_SITE_ZINDEX + 100
            });
        }
      });
      this._propertiesLayer.addListener('click', (event: google.maps.Data.MouseEvent) => {
        this.selectedHeritageSiteInfo = new HeritageSiteInfo(event);
        this.heritgeSiteSelected.emit(this.selectedHeritageSiteInfo);
        const feature = event ? event.feature : null;
        if (feature) {
          this.zone.run(() => this.onMarkerClick(this._propertiesLayer, event));
        }
      });
    }
  }



  /**
   * Updates styles applied to all GeoJSON features in the layer.
   */
  updateStyles(styles: LayerStyles) {
    if (!this.map) { return; }
    if (!styles.styleRules) {
      return;
    }
    if (styles.layer === 'Overlays') {
      this.styler.uncache();
      this._overlaysLayer.forEach((feature) => {
        const featureStyles = this.getStylesForFeature(feature, styles.styleRules);
        feature['zIndex'] = HERITAGE_OVERLAY_STYLE.zIndex;
        this._overlaysLayer.overrideStyle(feature, featureStyles);
        });
    } else if (styles.layer === 'Application_Number') {
      this.styler.uncache();
      this._planningLayer.forEach((feature) => {
        const featureStyles = this.getStylesForFeature(feature, styles.styleRules);
        feature['zIndex'] = HERITAGE_SITE_ZINDEX;
        this._planningLayer.overrideStyle(feature, featureStyles);
        });
    } else if (styles.layer === 'vhdplaceid') {
      this.styler.uncache();
      // console.time('styling');
      this._propertiesLayer.forEach((feature) => {
        const featureStyles = this.getStylesForFeature(feature, styles.styleRules);
        feature['zIndex'] = HERITAGE_SITE_ZINDEX;
        this._propertiesLayer.overrideStyle(feature, featureStyles);
        });
      // console.timeEnd('styling');
    }
  }

  /**
   * Returns applicable style rules for a given row.
   * @param row
   * @param styles
   */
  getStylesForFeature (feature: google.maps.Data.Feature, styles) {
    // Extract properties from feature instance.
    const properties = {};
    feature.forEachProperty((value, key) => {
      properties[key] = value;
    });

    // Parse styles.
    const featureStyles = {};
    StyleProps.forEach((styleprop) => {
      featureStyles[styleprop.name] = this.styler.parseStyle(styleprop.name, properties, styles[styleprop.name]);
    });

    // Maps API has no 'circleRadius' property, so create a scaled icon on the fly.
    const geometry = feature.getGeometry();
    const type = geometry && geometry.getType();
    if (type === 'Point' && featureStyles['circleRadius']) {
      featureStyles['icon'] = this.styler.getIcon(featureStyles['circleRadius'], featureStyles['fillColor'], featureStyles['fillOpacity']);
      delete featureStyles['circleRadius'];
    }
    return featureStyles;
  }
  /**
   * Displays info window for overlay. This is a dynamically created component.
   */
  onMarkerClick(_layer, event: google.maps.Data.MouseEvent) {

    const feature: google.maps.Data.Feature = event ? event.feature : null;

    if (feature) {
      const properties = {};
      const div = document.createElement('div'); // To place component into.
      if (this.infoWindow === null) {
        this.infoWindow = new google.maps.InfoWindow({
          content: 'Default'});
      }

      feature.forEachProperty((value, key) => {
        properties[key] = key === this._geoColumn ? truncateWKT(value) : value;
      });

      if (properties.hasOwnProperty('ZONE_DESCRIPTION')) {
        // Clicked on Overlay
        if (this.overlayInfoComponentRef) {
          this.overlayInfoComponentRef.destroy();
        }
        const compFactory = this.resolver.resolveComponentFactory(OverlayInfoComponent);
        this.overlayInfoComponentRef = compFactory.create(this.injector);

        this.highlightedOverlay = new OverlayProperties(event);
        this.overlayInfoComponentRef.instance.overlayProperties = this.highlightedOverlay;
        this.overlayInfoComponentRef.instance.title = 'Clicked Overlay';

        this.appRef.attachView(this.overlayInfoComponentRef.hostView);
        div.appendChild(this.overlayInfoComponentRef.location.nativeElement);

      } else if (properties.hasOwnProperty('vhdplaceid')) {
        /*
          const status = properties['HeritageStatus'];
          const htmlContentString = `
          <b>Removed ${status} site in ${properties['Overlay']} at</b><br/>
          Official Address: ${properties['EZI_ADD']}<br/>
          Matched using: ${properties['Matched']}<br/>
          Registered Address: ${properties['OriginalAddress']}<br/>
          VHD Location : ${properties['vhdLocation']}<br/>
          VHD placeId: ${properties['vhdPlacesId']}<br/>
          Matched using: ${properties['VHDMatched']}<br/>
          PROPERTY_PFI: ${properties['PROPERTY_PFI']}<br/>
          EZI_ADDRESS: ${properties['EZI_ADD']}<br/>
          `;
          this.infoWindow.setContent(htmlContentString);
          this.infoWindow.open(this.map);
          this.infoWindow.setPosition(event.latLng);
          */
      } else if (properties.hasOwnProperty('Application_Number')) {

        const status = properties['HeritageStatus'];
        const htmlContentString = `
        <b>${properties['Property_Address']}</b><br/>
        ${properties['Application_Number']}<br/>
        Received: ${properties['Date_Received']}<br/>
        Cost: ${properties['Estimated_Cost']}<br/>
        Decision: ${properties['Decision']}<br/>
        Status: ${properties['Application_Status']}<br/><br/>
        <span><b>Description:</b></span> ${properties['Description']}<br/><br/>
        <p data-status=${status} class="heritageStatusColor">${status}</p>
        `;
        this.infoWindow.setContent(htmlContentString);
        this.infoWindow.open(this.map, _layer);
        this.infoWindow.setPosition(event.latLng);
      }
    }
    // componentRef.instance.someObservableOrEventEmitter.subscribe(data => this.prop = data);
  }

  /**
   * Displays info window for selected feature.
   * @param feature
   * @param latLng
   */
  showInfoWindow_unused(event: any, latLng: google.maps.LatLng) {
    const feature: google.maps.Data.Feature = event ? event.feature : null;
    const properties = {};
    if (this.infoWindow === null) {
      this.infoWindow = new google.maps.InfoWindow({
        content: 'Default'});
    }

    if (feature) {
      feature.forEachProperty((value, key) => {
        properties[key] = key === this._geoColumn ? truncateWKT(value) : value;
      });
      if (properties.hasOwnProperty('vhdplaceid')) {
        const status = properties['HeritageStatus'];
        let htmlContentString = `
        <b>${properties['OriginalAddress']}</b><br/>
        <p data-status=${status} class="heritageStatusColor">${status}</p>
        In Heritage Overlay ${properties['Overlay']}
        <p>VHR ${properties['VHR']}</p>
        `;

        if (properties['SosHash'] !== 'null') {
          console.log(properties['SosHash']);
          htmlContentString += `
          <div><a target="_blank" href="${GCS_BUCKET_SOS}${properties['SosHash']}.html">Statement of Significance</a></div>`;
        }

        if (properties['Image'] !== 'null') {
          htmlContentString += `<img src="${properties['Image']}" alt="VHD Photo" height="60%" width="60%">`;
        }

        this.infoWindow.setContent(htmlContentString);

      } else if (properties.hasOwnProperty('Application_Number')) {
        const status = properties['HeritageStatus'];
        const htmlContentString = `
        <b>${properties['Property_Address']}</b><br/>
        ${properties['Application_Number']}<br/>
        <p data-status=${status} class="heritageStatusColor">${status}</p>
        In Heritage Overlay ${properties['Overlay']}
        <p>VHR ${properties['VHR']}</p>
        `;

        this.infoWindow.setContent(htmlContentString);

      } else {
        // this.infoWindow.setContent(`Heritage Overlay <b>${properties['Overlay']}</b>`);
        // this.infoWindow.setContent(`<app-overlay-info [overlayProperties]='overlayProperties'></app-overlay-info>`);
        // We need to run dynamic component  in angular2 zone
        this.zone.run(() => this.onMarkerClick(this._overlaysLayer, event));
      }
      this.infoWindow.open(this.map);
      this.infoWindow.setPosition(latLng);
    }
  }
}

function recursiveExtendBounds(geometry, callback, thisArg) {
  if (geometry == null) {
    return;
  }
  if (geometry instanceof google.maps.LatLng) {
    callback.call(thisArg, geometry);
  } else if (geometry instanceof google.maps.Data.Point) {
    callback.call(thisArg, geometry.get());
  } else {
    geometry.getArray().forEach(function(g) {
      recursiveExtendBounds(g, callback, thisArg);
    });
  }
}
function truncateWKT(text: string): string {
  text = String(text);
  return text.length <= 500 ? text : text.substr(0, 500) + '…';
}

