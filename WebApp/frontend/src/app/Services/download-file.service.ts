import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DownloadFileService {

  private _urlApi = 'http://localhost:5000/api/';

  constructor(private _http: HttpClient) { }

  getDeploymentLogs(protocolName: string): Observable<Blob> {
    const url = this._urlApi + 'deployment/downloadLog/' + protocolName;
    const httpOptions = { responseType: 'blob' as 'json'};
    return this._http.get<Blob>(url, httpOptions);
  }

  getDeploymentConf(protocolName: string): Observable<Blob> {
    const url = this._urlApi + 'deployment/downloadConf/' + protocolName;
    const httpOptions = { responseType: 'blob' as 'json'};
    return this._http.get<Blob>(url, httpOptions);
  }

  getExecutionLogs(protocolName: string): Observable<Blob> {
    const url = this._urlApi + 'execution/downloadLog/' + protocolName;
    const httpOptions = { responseType: 'blob' as 'json'};
    return this._http.get<Blob>(url, httpOptions);
  }

   getExecutionConf(protocolName: string): Observable<Blob> {
    const url = this._urlApi + 'execution/downloadConf/' + protocolName;
    const httpOptions = { responseType: 'blob' as 'json'};
    return this._http.get<Blob>(url, httpOptions);
  }
}
