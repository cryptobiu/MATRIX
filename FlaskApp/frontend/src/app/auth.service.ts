import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { filter } from 'rxjs/operators';
import * as auth0 from 'auth0-js';


@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private _idToken: string;
  private _accessToken: string;
  private _expiresAt: number;

  auth0 = new auth0.WebAuth(
    {
      clientID: 'YOUR_CLIENT_ID',
      domain: 'YOUR_AUTH0_DOMAIN',
      responseType: 'token id_token',
      redirectUri: 'http://localhost:3000/callback',
      scope: 'openid'
    }
  );

  constructor() {
    this._idToken = '';
    this._accessToken = '';
    this._expiresAt = 0;
  }

  get accessToken(): string {
    return this._accessToken;
  }

  get idToken(): string {
    return this._idToken;
  }

  public login(): void {
    this.auth0.authorize();
  }
}
