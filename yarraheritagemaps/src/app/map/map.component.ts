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

import { Component, ElementRef, Input, Output, EventEmitter, ViewChild, AfterViewInit } from '@angular/core';
import { StyleProps, StylesService, StyleRule, LayerStyles } from '../services/styles.service';
import * as parseWKT from 'wellknown';
import { OverlayProperties } from '../overlays';

declare var geoXML3: any;
import '../../../third_party/geocodezip/geoxml3';
import { style } from '@angular/animations';


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
  @ViewChild('mapEl') mapEl: ElementRef;
  @ViewChild('mouseinfo') mouseinfo: ElementRef;

  // Maps API instance.
  map: google.maps.Map;

  // Info window for display over Maps API.
  infoWindow: google.maps.InfoWindow;

  // Basemap styles.
  pendingStyles: Promise<Array<google.maps.MapTypeStyle>>;

  // Styling service.
  readonly styler = new StylesService();

  private _rows: Array<Object>;
  private _overlay_rows: Array<Object>;
  private _geoColumn: string;
  private _geodesicFeatures: Map<google.maps.Data.Feature, IFeature|Array<IFeature>> = new Map();
  private _overlaysLayer: google.maps.Data;
  private _propertiesLayer: google.maps.Data;
  private _mmbwLayer: google.maps.KmlLayer;
  private _mmbwGroundOverlay: google.maps.GroundOverlay;
  @Output() overlayChanged: EventEmitter<String> =   new EventEmitter();
  @Output() overlaySelected: EventEmitter<String> =   new EventEmitter();
  @Input() overlayInfo: String;

  @Input()
  set rows(rows: Array<Object>) {
    this._rows = rows;
    this.updateGeoJSON();
  }

  @Input()
  set geoColumn(geoColumn: string) {
    this._geoColumn = geoColumn;
    this.updateGeoJSON();
  }

  @Input()
  set styles(styles: LayerStyles) {
    this.updateStyles(styles);
  }

  constructor () {
    this.pendingStyles = fetch('assets/basemap.json', {credentials: 'include'})
      .then((response) => response.json());
  }

  /**
   * Constructs a Maps API instance after DOM has initialized.
   */
  ngAfterViewInit() {
    Promise.all([ pendingMap, this.pendingStyles ])
      .then(([_, mapStyles]) => {
        this._geoColumn = 'bndry';
        this.map = new google.maps.Map(this.mapEl.nativeElement, {center: {lat: -37.83433865, lng: 144.96147273999998}, zoom: 6});
        this.map.setOptions({styles: mapStyles});

        this.infoWindow = new google.maps.InfoWindow({content: ''});

        const bounds = new google.maps.LatLngBounds();
        bounds.extend(new google.maps.LatLng(-37.83433865, 144.96147273999998));
        bounds.extend(new google.maps.LatLng(-37.775308171, 145.03859800099997));
        this.map.fitBounds(bounds);

        this._overlaysLayer = new google.maps.Data();
        this._propertiesLayer = new google.maps.Data();

        const infowindow = new google.maps.InfoWindow({});
        const geoXml = new geoXML3.parser({
          map: this.map,
          infoWindow: infowindow,
          singleInfoWindow: true,
        });
        geoXml.parse('../../../assets/MMBW/MMBW_1264.kml');
      });
  }

  removeFeaturesFromLayer(layer) {
    layer.forEach((feature) => {
      if (Array.isArray(feature)) {
        feature.forEach((f) => {
          layer.remove(f);
        });
      } else {
        layer.remove(feature);
      }
    });
  }

  addResultsToLayer(layer, rows, zIndex) {

    rows.forEach((row) => {
      try {
        const geometry = parseWKT(row[this._geoColumn]);
        const feature = {type: 'Feature', geometry, properties: row, zIndex: zIndex};
        layer.addGeoJson(feature);

      } catch (e) {
        // Parsing can fail (e.g. invalid WKT); just log the error.
        console.error(e);
      }
    });
    layer.setMap(this.map);
  }

  /**
   * Converts row objects into GeoJSON, then loads into Maps API.
   */
  updateGeoJSON() {
    if (!this._rows || !this._geoColumn) { return; }

    const isZonelayer =  ('ZONE_CODE' in this._rows[0]) ? true : false;
    // this._overlaysLayer : this._propertiesLayer;

    if (isZonelayer) {
      // Update the Overlays Key Map
      this._overlay_rows = this._rows;
      this.addResultsToLayer(this._overlaysLayer, this._rows, 0);

      /*
      this._overlaysLayer.setStyle(function(feature:  google.maps.Data.Feature) {
          const ostyle = HERITAGE_OVERLAY_STYLE;

          if (feature.getProperty('higlighted') === 1 ) {
              ostyle.fillOpacity = HIGHLIGHTED_HERITAGE_OVERLAY_STYLE.fillOpacity;
          } else {
            ostyle.fillOpacity = HERITAGE_OVERLAY_STYLE.fillOpacity;
          }

          const trees = feature.getProperty('trees');
          if (trees === 'Yes') {
            ostyle.strokeColor = '#00FF00';
          } else {
            ostyle.strokeColor = '#0000FF';
          }
          console.log(trees);

          return ostyle;
      });
      */

      this._overlaysLayer.addListener('mouseover', (event) => {
        if (event.feature) {
          this.overlayInfo = event.feature.getProperty('HeritagePlace');
          const op = new OverlayProperties();
          op['Overlay'] = event.feature.getProperty('Overlay');
          op['HeritagePlace'] = event.feature.getProperty('HeritagePlace');
          op['PaintControls'] = event.feature.getProperty('PaintControls');
          op['InternalControls'] = event.feature.getProperty('InternalControls');
          op['TreeControls'] = event.feature.getProperty('TreeControls');
          op['FenceControls'] = event.feature.getProperty('FenceControls');
          op['VHR'] = event.feature.getProperty('VHR');
          op['AboriginalHeritagePlace'] = event.feature.getProperty('HeritagePlace');
          op['Status'] = event.feature.getProperty('Status');
          op['Expiry'] = event.feature.getProperty('Expiry');
          console.log(op);

          if (this.overlayInfo !== null) {
            this.overlayChanged.emit(this.overlayInfo );
          }
          this._overlaysLayer.overrideStyle(event.feature, {strokeWeight: 3});
        }
      });

      this._overlaysLayer.addListener('mouseout', (event) => {
        if (event.feature) {
          this.overlayInfo = ''; // event.feature.getProperty('ZONE_CODE');
          this.overlayChanged.emit(this.overlayInfo );
          this._overlaysLayer.overrideStyle(event.feature, {strokeWeight: 1});
        }
      });

      this._overlaysLayer.addListener('dblclick', (event) => {
        if (event.feature) {
          this.overlayInfo = event.feature.getProperty('ZONE_CODE');
          this.overlaySelected.emit(this.overlayInfo );
          this.overlayChanged.emit(this.overlayInfo );
        }
      });
      this._overlaysLayer.addListener('click', (e) => {
          google.maps.event.trigger(this._propertiesLayer, 'click', e);
      });

    } else {  // properties layer

      this._propertiesLayer.setMap(null);
      const bounds = new google.maps.LatLngBounds();

      this.removeFeaturesFromLayer(this._propertiesLayer); // remove property details from last render.
      const map = this.map;
      this._propertiesLayer.addListener('addfeature', function(e) {
        recursiveExtendBounds(e.feature.getGeometry(), bounds.extend, bounds);
        if (!bounds.isEmpty()) {
          map.fitBounds(bounds);
        }
      });
      this.addResultsToLayer(this._propertiesLayer, this._rows, 100);

      this._propertiesLayer.addListener('mouseover', (event) => {
        if (event.feature) {
          this._propertiesLayer.overrideStyle(event.feature, {
            strokeWeight: 3,
            zIndex: 200
          });
        }
      });

      this._propertiesLayer.addListener('mouseout', (event) => {
        if (event.feature) {
          this._propertiesLayer.overrideStyle(event.feature, {
              strokeWeight: 1,
              zIndex: 1
            });
        }
      });

      this._propertiesLayer.addListener('click', (e) => {
        const feature = e ? e.feature : null;
        if (feature) {
          this.showInfoWindow(feature, e.latLng);
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
        this._overlaysLayer.overrideStyle(feature, featureStyles);
        });
    } else if (styles.layer === 'HeritageStatus') {
      this.styler.uncache();
      this._propertiesLayer.forEach((feature) => {
        const featureStyles = this.getStylesForFeature(feature, styles.styleRules);
        this._propertiesLayer.overrideStyle(feature, featureStyles);
        });
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
   * Displays info window for selected feature.
   * @param feature
   * @param latLng
   */
  showInfoWindow (feature: google.maps.Data.Feature, latLng: google.maps.LatLng) {
    const properties = {};
    if (feature) {
      feature.forEachProperty((value, key) => {
        properties[key] = key === this._geoColumn ? truncateWKT(value) : value;
      });
      if (properties.hasOwnProperty('HeritageStatus')) {
        const status = properties['HeritageStatus'];
        this.infoWindow.setContent(`<b>${properties['NormalAddress']}</b><br/>
        <p data-status=${status} class="heritageStatusColor">${status}</p>
        In Heritage Overlay ${properties['Overlay']}
        `
        );

      } else {
        this.infoWindow.setContent(`Heritage Overlay <b>${properties['ZONE_CODE']}</b>`);
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
