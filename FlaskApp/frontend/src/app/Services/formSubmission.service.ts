import { Injectable } from '@angular/core';
import {HttpClient, HttpErrorResponse} from "@angular/common/http";
import {Protocol} from "../protocol";
import { catchError} from "rxjs/operators";
import {throwError} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class FormSubmissionService {

  _url = 'http://localhost:5000/protocols/registerProtocol';
  constructor(private _http: HttpClient) { }

  submitForm(protocol: Protocol){
    return this._http.post<any>(this._url, protocol).
    pipe(catchError(this.errorHandler))
  }

  errorHandler(error: HttpErrorResponse){
    return throwError(error);
  }
}
