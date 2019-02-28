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
    let _url = 'http://localhost:5000/api/protocols/registerProtocol';
    return this._http.post<any>(_url, protocol).
    pipe(catchError(this.handleError))
  }

  submitCompetitionRegistrationForm(cr: CompetitionRegistration, competitionName: string)
  {
    let _url = 'http://localhost:5000/api/competitions/registerCompetition/' + competitionName;
    return this._http.post<any>(_url, cr).
    pipe(catchError(this.handleError))
  }

  private handleError(error: HttpErrorResponse) {
  if (error.error instanceof ErrorEvent) {
    // A client-side or network error occurred. Handle it accordingly.
    console.error('An error occurred:', error.error.message);
  } else {
    // The backend returned an unsuccessful response code.
    // The response body may contain clues as to what went wrong,
    console.error(
      `Backend returned code ${error.status}, ` +
      `body error was: ${error.error}, ` +
      `body was:  ${error.message}`
      );
  }
  // return an observable with a user-facing error message
  return throwError(
    'Something bad happened; please try again later.' + error.message);
  }
}
