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
import { StyleProps, StylesService, StyleRule } from '../services/styles.service';
import * as parseWKT from 'wellknown';
import { HERITAGE_OVERLAY_STYLE, HIGHLIGHTED_HERITAGE_OVERLAY_STYLE } from '../app.constants';

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
  set styles(styles: Array<StyleRule>) {
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
        this.map = new google.maps.Map(this.mapEl.nativeElement, {center: {lat: -37.83433865, lng: 144.96147273999998}, zoom: 5});
        this.map.setOptions({styles: mapStyles});

        this.infoWindow = new google.maps.InfoWindow({content: ''});
        /*
        this.map.data.addListener('click', (e) => {
          this.showInfoWindow(e.feature, e.latLng);
        });
        */
        const bounds = new google.maps.LatLngBounds();
        bounds.extend(new google.maps.LatLng(-37.83433865, 144.96147273999998));
        bounds.extend(new google.maps.LatLng(-37.775308171, 145.03859800099997));
        this.map.fitBounds(bounds);
        this._overlaysLayer = new google.maps.Data();
        this._propertiesLayer = new google.maps.Data();
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

  // Convert to equivalent geodesic features.
  convertFeaturesToGeodesic(data) {

    const bounds = new google.maps.LatLngBounds();
    data.forEach((f: google.maps.Data.Feature) => {
      const g = f.getGeometry();

      if (!g) { return; }

      switch (g.getType()) {

        case 'Point':
        case 'MultiPoint':
          break;

        case 'LineString':
          data.overrideStyle(f, { visible: false, 'zIndex': 100 });
          this._geodesicFeatures.set(f, new google.maps.Polyline({
            path: (<google.maps.Data.LineString>g).getArray(),
            map: this.map,
            geodesic: true
          }));
          break;

        case 'MultiLineString':
          data.overrideStyle(f, { visible: false, 'zIndex': 100 });
          const polylinePathList = (<google.maps.Data.MultiLineString>g).getArray().map((line) => line.getArray());
          this._geodesicFeatures.set(f, polylinePathList.map((polylinePath) => new google.maps.Polyline({
            path: polylinePath,
            map: this.map,
            geodesic: true
          })));
          break;

        case 'Polygon':
          data.overrideStyle(f, { visible: false, 'zIndex': 100 });
          const paths = (<google.maps.Data.Polygon>g).getArray().map((ring) => ring.getArray());
          this._geodesicFeatures.set(f, new google.maps.Polygon({
            paths: paths,
            map: this.map,
            geodesic: true
          }));
          break;

        case 'MultiPolygon':
          data.overrideStyle(f, { visible: false, 'zIndex': 100 });
          const polygonPathsList = (<google.maps.Data.MultiPolygon>g).getArray()
            .map((polygon) => polygon.getArray().map((ring) => ring.getArray()));
          this._geodesicFeatures.set(f, polygonPathsList.map((polygonPaths) => new google.maps.Polygon({
            paths: polygonPaths,
            map: this.map,
            geodesic: true
          })));
          break;

        default:
          console.warn(`Geodesic conversion not yet implemented for type "${g.getType()}".`);
      }

      // Add event listeners to converted features.
      if (this._geodesicFeatures.has(f)) {
        let geometries = this._geodesicFeatures.get(f);
        geometries = Array.isArray(geometries) ? geometries : [geometries];
        geometries.forEach((geom) => {
          geom.addListener('click', (e) => this.showInfoWindow(f, e.latLng));
        });
        console.log('add click');
      } else {
        console.log('no click');
      }
      recursiveExtendBounds(g, bounds.extend, bounds);
    });

    if (!bounds.isEmpty()) {
      this.map.fitBounds(bounds);
    }
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
      // this.convertFeaturesToGeodesic(this._overlaysLayer) ;

      this._overlaysLayer.setStyle(function(feature:  google.maps.Data.Feature) {
          return feature.getProperty('higlighted') === 1 ? HIGHLIGHTED_HERITAGE_OVERLAY_STYLE : HERITAGE_OVERLAY_STYLE;
      });

      this._overlaysLayer.addListener('mouseover', (event) => {
        if (event.feature) {
          this.overlayInfo = event.feature.getProperty('ZONE_CODE');
          this.overlayChanged.emit(this.overlayInfo );
          event.feature.setProperty('higlighted', 1);
        }
      });
      this._overlaysLayer.addListener('mouseout', (event) => {
        if (event.feature) {
          this.overlayInfo = ''; // event.feature.getProperty('ZONE_CODE');
          this.overlayChanged.emit(this.overlayInfo );
          event.feature.setProperty('higlighted', 0);
        }
      });
      this._overlaysLayer.addListener('dblclick', (event) => {
        if (event.feature) {
          this.overlayInfo = event.feature.getProperty('ZONE_CODE');
          this.overlaySelected.emit(this.overlayInfo );
          this.overlayChanged.emit(this.overlayInfo );
          // console.log('Selected ' +  this.overlayInfo);
        }
      });
      this._overlaysLayer.addListener('click', (e) => {
          console.error('DEBUG: Clicked on Heritage Underlay ' + e.feature.getProperty('ZONE_DESC'));
          google.maps.event.trigger(this._propertiesLayer, 'click', e);
      });

    } else {  // properties layer
      this._propertiesLayer.setMap(null);
      this.removeFeaturesFromLayer(this._propertiesLayer); // remove property details from last render.
      this.addResultsToLayer(this._propertiesLayer, this._rows, 100);
      this._propertiesLayer.addListener('click', (e) => {
        console.error('DEBUG: Clicked Property ' + e );
        const feature = e ? e.feature : null;
        if (feature) {
          this.showInfoWindow(feature, e.latLng);
        }
      });
    }
  }

  /**
   * Updates styles applied to all GeoJSON features.
   */
  updateStyles(styles: Array<StyleRule>) {
    if (!this.map) { return; }
    this.styler.uncache();
    this._propertiesLayer.forEach((feature) => {
      const featureStyles = this.getStylesForFeature(feature, styles);
      if (this._geodesicFeatures.has(feature)) {
        const geodesicFeature = this._geodesicFeatures.get(feature);
        if (Array.isArray(geodesicFeature)) {
          geodesicFeature.forEach((f) => f.setOptions(featureStyles));
        } else {
          (<google.maps.Polyline> geodesicFeature).setOptions(featureStyles);
        }
      } else {
        this._propertiesLayer.overrideStyle(feature, featureStyles);
      }
    });
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
    StyleProps.forEach((style) => {
      featureStyles[style.name] = this.styler.parseStyle(style.name, properties, styles[style.name]);
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
      this.infoWindow.setContent(`<pre>${JSON.stringify(properties, null, 2)}</pre>`);
      this.infoWindow.open(this.map);
      this.infoWindow.setPosition(latLng);
    } else {
      console.log('not a feature');
    }
  }
}

function recursiveExtendBounds(geometry: any, callback: Function, self) {
  if (geometry instanceof google.maps.LatLng) {
    callback.call(self, geometry);
  } else if (geometry instanceof google.maps.Data.Point) {
    callback.call(self, geometry.get());
  } else {
    geometry.getArray().forEach((g) => {
      recursiveExtendBounds(g, callback, self);
    });
  }
}

function truncateWKT(text: string): string {
  text = String(text);
  return text.length <= 500 ? text : text.substr(0, 500) + '…';
}
