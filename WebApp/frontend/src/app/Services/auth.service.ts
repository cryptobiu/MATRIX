import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { filter } from 'rxjs/operators';
import * as auth0 from 'auth0-js';
import {Observable, Observer, Subject} from "rxjs";


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

  constructor(public router : Router) {
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

  public handleAuthentication(): void
  {
    this.auth0.parseHash((err, authResult) => {
      if(authResult && authResult.accessToken && authResult.idtoken){
        window.location.hash = '';
        this.localLogin(authResult);
        this.router.navigate(['/']);
      } else if (err)
      {
        this.router.navigate(['/']);
        console.log(err);
      }
    });
  }

  private localLogin(authResult){
    localStorage.setItem('isLoggedIn', 'true');
    const expiresAt = (authResult.expiresIn * 3600) + new Date().getTime();
    this._accessToken = authResult.accessToken;
    this._idToken = authResult.idToken;
    this._expiresAt = expiresAt;
  }

  public renewTokens(): void {
    this.auth0.checkSession({}, (err, authResult) => {
      if(authResult && authResult.accessToken && authResult.idtoken)
        this.localLogin(authResult);
       else if (err)
      {
        console.log(err);
        this.logout();
      }
    });
  }

  public logout(): void{
    this._accessToken = '';
    this._idToken = '';
    this._expiresAt = 0;
    // Remove isLoggedIn flag from localStorage
    localStorage.removeItem('isLoggedIn');
    // Go back to the home route
    this.router.navigate(['/']);
  }

  public isAuthenticated(): boolean {
    // Check whether the current time is past the
    // access token's expiry time
    return new Date().getTime() < this._expiresAt;
  }

}
