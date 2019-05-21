import { HttpClient } from '@angular/common/http';
import { Injectable, OnInit } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { Subject } from 'rxjs/Subject';

export interface LayerDescription {
    name: string | undefined;
    description: string | undefined;
}

import {
    map,
    catchError,
    debounceTime,
} from 'rxjs/operators';


/**
 * Utility class for returing the available layers and some metadata.
 * For now returns a fixed list, but can later be replaced by a remote API.
 */
@Injectable()
export class LayersInfoService implements OnInit {
    $layerDescriptions = new Subject<LayerDescription>();

    /* Mocked layers can be replaced by RPC */
    private _layers: LayerDescription[] = [
        {
            name: 'Overlays',
            description: 'Heritage Overlay Boundaries'
        },
        {
            name: 'Sites',
            description: 'Individual Heritage Properties'
        },
        {
            name: 'MMBW',
            description: 'MMBW Maps drawn around 1900'
        },
        {
            name: 'Planning',
            description: 'Planning permit applications and approvals'
        }
    ];

    constructor(private http: HttpClient) {
        this._layers.forEach(element => {
            this.$layerDescriptions.next(element);
        });
    }

    ngOnInit() {
    }

    getLayers(): Observable<LayerDescription> {
        return this.$layerDescriptions; // for Observable
    }

    getLayersStatic(): Array<LayerDescription> {
        return this._layers; // for mock
    }

}
