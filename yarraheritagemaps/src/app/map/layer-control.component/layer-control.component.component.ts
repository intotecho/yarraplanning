/*
 * Component for form to hide or show layers returns from LayersInfoService
 */


import { Component, OnInit, Output, EventEmitter, Input } from '@angular/core';
import { LayerDescription, LayersInfoService } from '../../../../src/app/services/layers-info-service';
import {FormControl} from '@angular/forms';

@Component({
  selector: 'app-layer-select',
  templateUrl: './layer-control.component.component.html',
  styleUrls: ['./layer-control.component.component.css']
})
export class LayerSelectComponent implements OnInit {
  layersForm = new FormControl();
  availableLayersInfo: Array<LayerDescription>;
  initalSelectionLayersInfo: Array<string>;
  formLayersInfo: Array<string>;
  private _selectedLayersInfo: LayerDescription[] = new Array<LayerDescription>(null);
  @Output() selectedLayersInfo: EventEmitter<Array<LayerDescription>> =   new EventEmitter();

  constructor(
    private layerInfoService: LayersInfoService
  ) {
   }

  ngOnInit() {
    /*
     this.layerInfoService.getLayers().subscribe((data: LayerDescription) => {
      this._layersInfo.push(data);
     });
    this.availableLayersInfo = this.layerInfoService.getLayersStatic().map(layer => layer.name);
    */
    this.availableLayersInfo = this.layerInfoService.getLayersStatic();
    this.formLayersInfo = this.availableLayersInfo.map(layer => layer.name);
    this.initalSelectionLayersInfo = this.formLayersInfo.slice(); // map(layer => layer.name);
    // this.layersForm.setValue(this.initalSelectionLayersInfo);
    this.layersForm.valueChanges.debounceTime(200).subscribe(() => {
      this._selectedLayersInfo = this.availableLayersInfo.filter((layer) => {
         return  this.layersForm.value.includes(layer.name);
      });
      console.log(this._selectedLayersInfo);
      this.selectedLayersInfo.emit(this._selectedLayersInfo);
    });


  }
}
