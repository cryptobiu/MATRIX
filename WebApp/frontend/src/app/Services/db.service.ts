import {Injectable} from '@angular/core';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {Observable, throwError} from "rxjs";
import {ICompetition, IProtocol} from "../interfaces";
import {catchError} from "rxjs/operators";

@Injectable({
  providedIn: 'root'
})
export class DbService {

  private _urlApi: string = 'http://localhost:5000/api/';

  constructor(private _http:HttpClient) { }

  getCompetitions(): Observable<ICompetition[]> {
    let url = this._urlApi + 'competitions';
    return this._http.get<ICompetition[]>(url).pipe(catchError(this.handleError));
  }

  getCompetition(competitionName: string)
  {
    let url = this._urlApi + 'competitions/' + competitionName;
    return this._http.get<ICompetition>(url).pipe(catchError(this.handleError));
  }

  getProtocols(): Observable<IProtocol[]> {
    let url = this._urlApi + 'protocols';
    return this._http.get<IProtocol[]>(url).pipe(catchError(this.handleError));
  }

  executeDeployOperation(protocolName: string, operation:string) {
    let url = this._urlApi + 'deploy/' + protocolName + '/' + operation;
    return this._http.get(url).pipe(catchError(this.handleError));
  }

  executeExecutionOperation(protocolName: string, operation:string) {
    let url = this._urlApi + 'execute/' + protocolName + '/' + operation;
    return this._http.get(url).pipe(catchError(this.handleError));
  }

  executeReportingOperation(protocolName: string, operation:string) {
    let url = this._urlApi + 'reporting/' + protocolName + '/' + operation;
    return this._http.get(url).pipe(catchError(this.handleError));
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
