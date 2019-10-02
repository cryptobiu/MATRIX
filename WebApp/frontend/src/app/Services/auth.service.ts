import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import * as auth0 from 'auth0-js';
import auth0Tokens from 'assets/auth0Tokens.json';

(window as any).global = window;

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private _idToken: string;
  private _accessToken: string;
  private _expiresAt: number;
  private _auth0: auth0.WebAuth;
  private _authenticated: boolean;
  private _userProfile: any;


  constructor(public router: Router) {
    this._idToken = '';
    this._accessToken = '';
    this._expiresAt = 0;
    this._auth0 = new auth0.WebAuth(
    {
      clientID: auth0Tokens.clientID,
      domain: auth0Tokens.domain,
      responseType: 'token id_token',
      redirectUri: auth0Tokens.redirectUri,
      scope: 'openid'
    });
  }

  get accessToken(): string {
    return this._accessToken;
  }

  get idToken(): string {
    return this._idToken;
  }

  public login(): void {
    console.log(this._auth0.authorize());
    this._authenticated = this._auth0.authenticated;
  }

   handleLoginCallback() {
    // When Auth0 hash parsed, get profile
    this._auth0.parseHash((err, authResult) => {
      if (authResult && authResult.accessToken) {
        window.location.hash = '';
        this.getUserInfo(authResult);
        this.router.navigate(['/']).catch(function (err) {
          if(err)
            console.error(err);
        });
      } else if (err) {
        console.error(`Error: ${err.error}`);
      }
      this.router.navigate(['/']).catch(function (err) {
        if(err)
          console.error(err);
      });
    });
  }

  getUserInfo(authResult) {
    // Use access token to retrieve user's profile and set session
    this._auth0.client.userInfo(authResult.accessToken, (err, profile) => {
      if (profile) {
        this._setSession(authResult, profile);
      }
    });
  }

   private _setSession(authResult, profile) {
    // Save authentication data and update login status subject
    this._expiresAt = authResult.expiresIn * 1000 + Date.now();
    this._accessToken = authResult.accessToken;
    this._userProfile = profile;
    this._authenticated = true;
    localStorage.setItem('isLoggedIn', 'true');
    localStorage.setItem('clientToken', this._accessToken);
  }

  public logout(): void{
    this._accessToken = '';
    this._idToken = '';
    this._expiresAt = 0;
    // Remove isLoggedIn flag from localStorage
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('clientToken');
    // Go back to the home route
    this._auth0.logout({
      returnTo: 'http://localhost:4200',
    });
  }


  public isAuthenticated(): boolean {
    // Check whether the current time is past the
    // access token's expiry time
    return this._authenticated;
  }

}
