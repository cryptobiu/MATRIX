import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule, routingComponents } from './app-routing.module';
import { AppComponent } from './app.component';
import { PageNotFoundComponent } from './page-not-found/page-not-found.component';
import { HomeComponent } from './home/home.component';
import { CompetitionsDetailsComponent } from './competitions-details/competitions-details.component';
import { LoginComponent } from './login/login.component';
import { HttpModule } from '@angular/http';
import { HttpClientModule } from '@angular/common/http';
import { ProtocolsComponent } from './protocols/protocols.component'

@NgModule({
  declarations: [
    AppComponent,
    routingComponents,
    PageNotFoundComponent,
    HomeComponent,
    CompetitionsDetailsComponent,
    LoginComponent,
    ProtocolsComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    HttpModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
