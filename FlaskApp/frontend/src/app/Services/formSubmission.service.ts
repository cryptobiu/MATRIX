import { Injectable } from '@angular/core';
import {HttpClient, HttpErrorResponse} from "@angular/common/http";
import {Protocol, CompetitionRegistration} from "../classes";
import { catchError} from "rxjs/operators";
import {throwError} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class FormSubmissionService {

  constructor(private _http: HttpClient) { }

  submitUploadProtocolForm(protocol: Protocol){
    let _url = 'http://localhost:5000/protocols/registerProtocol';
    return this._http.post<any>(_url, protocol).
    pipe(catchError(this.errorHandler))
  }

  errorHandler(error: HttpErrorResponse){
    return throwError(error);
  }

  submitcompetitionRegistrationForm(cr: CompetitionRegistration)
  {
    let _url = 'http://localhost:5000/competitions/registerCompetition';
    return this._http.post<any>(_url, cr).
    pipe(catchError(this.errorHandler))
  }
}
