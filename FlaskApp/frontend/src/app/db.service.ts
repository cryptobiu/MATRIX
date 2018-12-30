import {Injectable, NgModule} from '@angular/core';
import {HttpClient, HttpClientModule} from '@angular/common/http';
import { CommonModule } from '@angular/common';
import {AppComponent} from "./app.component";
import {Observable} from "rxjs";
import {ICompetition} from "./competition";


@NgModule({
  imports: [CommonModule, HttpClientModule],
  exports: [],
  declarations: [ AppComponent ],
  bootstrap:    [ AppComponent ]
})

@Injectable({
  providedIn: 'root'
})
export class CompetitionService {

  private _getUrl: string = 'http://localhost:5000/competitions';
  // constructor(private _http:Http) { }
  constructor(private _http:HttpClient) { }

  getCompetitions(): Observable<ICompetition[]> {
    return this._http.get<ICompetition[]>(this._getUrl)
  }
}
