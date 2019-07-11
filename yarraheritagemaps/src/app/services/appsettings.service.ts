import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AppSettings {
  private _selectedShadingScheme: string;
  public get selectedShadingScheme() { return this._selectedShadingScheme; }
  public set selectedShadingScheme(newValue) {
    this._selectedShadingScheme = newValue;
    this.saveAppSettings();
  }

  private _advancedControlsOpened: boolean;
  public get advancedControlsOpened() { return this._advancedControlsOpened; }
  public set advancedControlsOpened(newValue) {
    this._advancedControlsOpened = newValue;
    this.saveAppSettings();
  }

  private _loadSitesForPreviousOverlay: boolean;
  public get loadSitesForPreviousOverlay() { return this._loadSitesForPreviousOverlay; }
  public set loadSitesForPreviousOverlay(newValue: boolean) {
    this._loadSitesForPreviousOverlay = newValue;
    this.saveAppSettings();
  }

  private _mapCenter: google.maps.LatLng;
  public get mapCenter() { return this._mapCenter; }
  public set mapCenter(newValue) {
    this._mapCenter = newValue;
    this.saveAppSettings();
  }

  private _mapZoom: number;
  public get mapZoom() { return this._mapZoom; }
  public set mapZoom(newValue) {
    this._mapZoom = newValue;
    this.saveAppSettings();
  }


  private _isInit = false;

  constructor () {
      this.readAppSettings();
  }

  readAppSettings() {
    const appSettingsString = localStorage.getItem('appSettings');
    if (appSettingsString) {
      const object: any =  JSON.parse(appSettingsString);
      this._advancedControlsOpened   = object['_advancedControlsOpened'];
      this._selectedShadingScheme = object['_selectedShadingScheme'] || 'Heritage Status';
      this._loadSitesForPreviousOverlay = object['_loadSitesForPreviousOverlay'] ? true : false;
      this._mapCenter = object['_mapCenter'] || new google.maps.LatLng(-37.83433865, 144.96147273999998);
      this._mapZoom = object['_mapZoom'] || 6;
    }
    this._isInit = true;
  }

  saveAppSettings() {
    if (this._isInit) {
      localStorage.setItem('appSettings',  JSON.stringify(this));
    }
  }
}
