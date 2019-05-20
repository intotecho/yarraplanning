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

import { Component, Renderer2, ChangeDetectorRef, NgZone, OnInit, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, FormControl, FormArray, Validators } from '@angular/forms';
import { MatTableDataSource, MatSnackBar } from '@angular/material';
import { StepperSelectionEvent } from '@angular/cdk/stepper';
import { Subject } from 'rxjs/Subject';
import { Subscription } from 'rxjs/Subscription';
import 'rxjs/add/operator/debounceTime';
import 'rxjs/add/operator/map';

import { StyleProps, StyleRule, LayerStyles } from '../services/styles.service';
import { BigQueryService, ColumnStat, Project } from '../services/bigquery.service';

import {
  Step,
  HERITAGE_SITE_QUERY,
  OVERLAYS_QUERY,
  HERITAGE_SITE_FILL_COLOR,
  OVERLAY_FILL_COLOR,
  OVERLAY_FILL_OPACITY,
  OVERLAY_STROKE_COLOR,
  OVERLAY_STROKE_OPACITY,
  HERITAGE_SITE_FILL_OPACITY,
  MAX_RESULTS_PREVIEW,
  HERITAGE_SITE_CIRCLE_RADIUS,
  HERITAGE_SITE_PROJECT_ID,
  HERITAGE_SITE_DATACENTER,
  HERITAGE_SITE_STROKE_COLOR,
} from '../app.constants';

import {
  matchingHeritageOverlays,
  HeritageOverlay,
  OverlayProperties
} from './panels/overlays-properties';

import {
  SelectMMBWOverlay, MMBWMapsLibrary
} from '../select-MMBWOverlay';


import { query } from '@angular/animations';
import { HeritageSiteInfo } from './panels/heritage-site-info/heritage-site-info';
const DEBOUNCE_MS = 1000;

@Component({
  selector: 'app-main',
  templateUrl: './main.component.html',
  styleUrls: ['./main.component.css']
})
export class MainComponent implements OnInit, OnDestroy {
  readonly title = 'Heritage Maps';
  readonly StyleProps = StyleProps;

  // GCP session data
  readonly dataService = new BigQueryService();
  isSignedIn: boolean;
  user: Object;
  matchingProjects: Array<Project> = [];
  matchingOverlays = matchingHeritageOverlays;
  overlayProperties: OverlayProperties = new OverlayProperties(null);
  selectedOverlayProperties: OverlayProperties = new OverlayProperties(null);

  selectedHeritageSiteInfo: HeritageSiteInfo = new HeritageSiteInfo(null);
  highlightedHeritageSiteInfo: HeritageSiteInfo = new HeritageSiteInfo(null);

  mmbwMaps: Array<SelectMMBWOverlay> = MMBWMapsLibrary;
  selectedMmbwMaps: Array<SelectMMBWOverlay> = [];
  // Form groups
  dataFormGroup: FormGroup;
  schemaFormGroup: FormGroup;
  stylesFormGroup: FormGroup;

  // BigQuery response data
  columns: Array<Object>;
  columnNames: Array<string>;
  bytesProcessed: Number = 0;
  lintMessage: String = '';
  pending = false;
  rows: Array<Object>;
  data: MatTableDataSource<Object>;
  stats: Map<String, ColumnStat> = new Map();
  mapsLib = [];

  // UI state
  stepIndex: Number = 0;

  // Current style rules
  // styles: Array<StyleRule> = [];
  styles: LayerStyles = new LayerStyles();

  // CodeMirror configuration
  readonly cmConfig = {
    indentWithTabs: true,
    smartIndent: true,
    lineNumbers: true,
    lineWrapping: true
  };
  readonly cmDebouncer: Subject<string> = new Subject();
  cmDebouncerSub: Subscription;

  constructor(
    private _formBuilder: FormBuilder,
    private _renderer: Renderer2,
    private _snackbar: MatSnackBar,
    private _changeDetectorRef: ChangeDetectorRef,
    private _ngZone: NgZone) {

    // Debounce CodeMirror change events to avoid running extra dry runs.
    this.cmDebouncerSub = this.cmDebouncer
      .debounceTime(DEBOUNCE_MS)
      .subscribe((value: string) => { this._dryRun(); });

    // Set up BigQuery service.
    this.dataService.onSigninChange(() => this.onSigninChange());
    this.dataService.init()
      .catch((e) => this.showMessage(parseErrorMessage(e)));
  }

  ngOnInit() {
    this.columns = [];
    this.columnNames = [];
    this.rows = [];
    // Data form group
    this.dataFormGroup = this._formBuilder.group({
      selectedMMBWIds: [],
      overlayId: ['HO0'],
      projectID: [HERITAGE_SITE_PROJECT_ID, Validators.required],
      sql: [OVERLAYS_QUERY
      , Validators.required],
      location: [HERITAGE_SITE_DATACENTER],
    });

    this.dataFormGroup.controls.projectID.valueChanges.debounceTime(200).subscribe(() => {
      this.dataService.getProjects()
        .then((projects) => {
          this.matchingProjects = projects.filter((project) => {
            return project['id'].indexOf(this.dataFormGroup.controls.projectID.value) >= 0;
          });
        });
    });


    this.dataFormGroup.controls.overlayId.valueChanges.debounceTime(200).subscribe(() => {
      this.dataFormGroup.patchValue({ sql: HERITAGE_SITE_QUERY });
      this.query(); // kick off inital query to load the overlays
    });

    this.dataFormGroup.controls.selectedMMBWIds.valueChanges.debounceTime(200).subscribe(() => {
      this.selectedMmbwMaps = this.mmbwMaps.filter((mmbwMap) => {
         return  this.dataFormGroup.controls.selectedMMBWIds.value.includes(mmbwMap.MMBWmapId);
      });
      console.log(this.selectedMmbwMaps);
    });

    // Schema form group
    this.schemaFormGroup = this._formBuilder.group({ geoColumn: [''] });

    // Style rules form group
    const stylesGroupMap = {};
    StyleProps.forEach((prop) => stylesGroupMap[prop.name] = this.createStyleFormGroup());
    this.stylesFormGroup = this._formBuilder.group(stylesGroupMap);
    this.stylesFormGroup.valueChanges.debounceTime(500).subscribe(() => this.updateStyles(''));

  }


  ngOnDestroy() {
    this.cmDebouncerSub.unsubscribe();
  }

  signin() {
    this.dataService.signin();
  }

  signout() {
    this.dataService.signout();
  }


  onSigninChange() {
    this._ngZone.run(() => {
      this.isSignedIn = this.dataService.isSignedIn;
      if (!this.dataService.isSignedIn) { return; }
      this.user = this.dataService.getUserEmail();
      this.dataService.getProjects()
        .then((projects) => {
          this.matchingProjects = projects;
          this._changeDetectorRef.detectChanges();
        });
      this.query(); // kick off inital query to load the overlays

    });
  }

  handleMapOverlayHighlighted(event) {
    this.overlayProperties = event;
  }

  handleMapOverlaySelected(event) {
    this.overlayProperties = event;
    this.selectedOverlayProperties = event;
    localStorage.setItem('selectedOverlay',  JSON.stringify(this.overlayProperties));
    this.dataFormGroup.patchValue({overlayId: this.overlayProperties.Overlay });
  }


  handleMapHeritageSiteHighlighted(event) {
    this.highlightedHeritageSiteInfo = event;
  }

  handleMapHeritageSiteSelected(event) {
    this.highlightedHeritageSiteInfo = event;
    this.selectedHeritageSiteInfo = event;
    localStorage.setItem('selectedProperty',  JSON.stringify(this.selectedHeritageSiteInfo));
    // this.dataFormGroup.patchValue({overlayId: this.overlayProperties.Overlay });
  }



  onStepperChange(e: StepperSelectionEvent) {
    this.stepIndex = e.selectedIndex;
    this.updateStyles('');

    gtag('event', 'step', { event_label: `step ${this.stepIndex}` });
  }

  dryRun() {
    this.cmDebouncer.next();
  }

  _dryRun() {
    const { overlayId, projectID, sql, location } = this.dataFormGroup.getRawValue();
    this.dataService.prequery(overlayId, projectID, sql, location)
      .then((bytesProcessed) => {
        this.bytesProcessed = bytesProcessed;
        this.lintMessage = '';
      })
      .catch((e) => {
        this.bytesProcessed = -1;
        this.lintMessage = parseErrorMessage(e);
      });
  }

  updateOverlayNames() {
      const queriedHeritageOverlays: Array<HeritageOverlay> = [];
      const rows = this.rows;

      // Get selection from previous session to initialise.
      const lastSelectedOverlay: OverlayProperties = JSON.parse(localStorage.getItem('selectedOverlay'));

      for (let i = 0; i < rows.length; i++) {
            const ovl: HeritageOverlay = {
              'ZONE_CODE': rows[i]['ZONE_CODE'],
              'ZONE_DESC': rows[i]['ZONE_DESC']
            };
            queriedHeritageOverlays.push(ovl);
            if (lastSelectedOverlay.Overlay === ovl.ZONE_CODE) {
              this.overlayProperties = lastSelectedOverlay;
              this.dataFormGroup.patchValue({overlayId: this.overlayProperties.Overlay });
            }
      }
      this.matchingOverlays = queriedHeritageOverlays;
  }

  query() {
    if (this.pending) { return; }
    this.pending = true;

    const { overlayId, projectID, sql, location } = this.dataFormGroup.getRawValue();

    this.dataService.query(overlayId, projectID, sql, location)
      .then(({ columns, columnNames, rows, stats }) => {
        this.columns = columns;
        this.columnNames = columnNames;
        this.rows = rows;
        this.stats = stats;
        this.data = new MatTableDataSource(rows.slice(0, MAX_RESULTS_PREVIEW));
        if (this.columnNames.find(h => h === 'ZONE_CODE')) {
            this.updateOverlayNames();
            // setup custom styling
            this.setNumStops(<FormGroup>this.stylesFormGroup.controls.fillColor, OVERLAY_FILL_COLOR.domain.length);
            this.setNumStops(<FormGroup>this.stylesFormGroup.controls.strokeColor, OVERLAY_STROKE_COLOR.domain.length);
            this.stylesFormGroup.controls.fillColor.patchValue(OVERLAY_FILL_COLOR);
            this.stylesFormGroup.controls.fillOpacity.patchValue(OVERLAY_FILL_OPACITY);
            this.stylesFormGroup.controls.strokeColor.patchValue(OVERLAY_STROKE_COLOR);
            this.stylesFormGroup.controls.strokeOpacity.patchValue(OVERLAY_STROKE_OPACITY);

            this.updateStyles('Overlays');
            this.showMessage('Double Click an Overlay on the map for more details', 5000);

          } else if (this.columnNames.find(h => h === 'HeritageStatus')) {
            this.setNumStops(<FormGroup>this.stylesFormGroup.controls.fillColor, HERITAGE_SITE_FILL_COLOR.domain.length);
            this.stylesFormGroup.controls.fillOpacity.patchValue(HERITAGE_SITE_FILL_OPACITY);
            this.stylesFormGroup.controls.fillColor.patchValue(HERITAGE_SITE_FILL_COLOR);
            this.stylesFormGroup.controls.strokeColor.patchValue(HERITAGE_SITE_STROKE_COLOR);
            this.updateStyles('HeritageStatus');
            this.showMessage('Showing Heritage properties within Selected Overlay', 5000);
          }
      })
      .catch((e) => {
        this.showMessage(parseErrorMessage(e));
      })
      .then(() => {
        this.pending = false;
        this._changeDetectorRef.detectChanges();
      });
  }

  updateStyles(layer: String) {
    if (this.stylesFormGroup.invalid) {
      console.log('invalid style');
      return;
    }
    const styles = new LayerStyles();
    styles.styleRules = this.stylesFormGroup.getRawValue();
    styles.layer = layer;
    this.styles = styles;
  }

  getRowWidth() {
    return (this.columns.length * 100) + 'px';
  }

  onFillPreset() {
    switch (this.stepIndex) {
      case Step.DATA:
        this.dataFormGroup.patchValue({ sql: HERITAGE_SITE_QUERY });
        break;
      case Step.SCHEMA:
        this.schemaFormGroup.patchValue({ geoColumn: 'WKT', latColumn: 'lat_avg', lngColumn: 'lng_avg' });
        break;
      case Step.STYLE:
        this.setNumStops(<FormGroup>this.stylesFormGroup.controls.fillColor, HERITAGE_SITE_FILL_COLOR.domain.length);
        this.setNumStops(<FormGroup>this.stylesFormGroup.controls.circleRadius, HERITAGE_SITE_CIRCLE_RADIUS.domain.length);
        this.stylesFormGroup.controls.fillOpacity.patchValue(HERITAGE_SITE_FILL_OPACITY);
        this.stylesFormGroup.controls.fillColor.patchValue(HERITAGE_SITE_FILL_COLOR);
        this.stylesFormGroup.controls.circleRadius.patchValue(HERITAGE_SITE_CIRCLE_RADIUS);
        break;
      default:
        console.warn(`Unexpected step index, ${this.stepIndex}.`);
    }

    gtag('event', 'preset', { event_label: `step ${this.stepIndex}` });
  }

  setNumStops(group: FormGroup, numStops: number): void {
    const domain = <FormArray>group.controls.domain;
    const range = <FormArray>group.controls.range;
    while (domain.length !== numStops) {
      if (domain.length < numStops) {
        domain.push(new FormControl(''));
        range.push(new FormControl(''));
      }
      if (domain.length > numStops) {
        domain.removeAt(domain.length - 1);
        range.removeAt(range.length - 1);
      }
    }
  }

  createStyleFormGroup(): FormGroup {
    return this._formBuilder.group({
      isComputed: [false],
      value: [''],
      property: [''],
      function: [''],
      domain: this._formBuilder.array([[''], ['']]),
      range: this._formBuilder.array([[''], ['']])
    });
  }

  getPropStatus(propName: string): string {
    const rule = <StyleRule>this.stylesFormGroup.controls[propName].value;
    if (!rule.isComputed && rule.value) { return 'global'; }
    if (rule.isComputed && rule.function) { return 'computed'; }
    return 'none';
  }

  getPropStats(propName: string): ColumnStat {
    const group = <FormGroup>this.stylesFormGroup.controls[propName];
    const rawValue = group.value;
    if (!rawValue.property) { return null; }
    return this.stats.get(rawValue.property);
  }

  getPropFormGroup(propName: string): FormGroup {
    return <FormGroup>this.stylesFormGroup.controls[propName];
  }

  showMessage(message: string, duration: number = 5000) {
    console.warn(message);
    this._ngZone.run(() => {
      this._snackbar.open(message, undefined, { duration: duration });
    });
  }
}

function parseErrorMessage (e, defaultMessage = 'Something went wrong') {
  if (e.message) { return e.message; }
  if (e.result && e.result.error && e.result.error.message) {
    return e.result.error.message;
  }
  return defaultMessage;
}
