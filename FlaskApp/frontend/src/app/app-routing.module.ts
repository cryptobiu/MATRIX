import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {CompetitionsComponent} from "./competitions/competitions.component";
import {CircuitsComponent} from "./circuits/circuits.component";
import {PageNotFoundComponent} from "./page-not-found/page-not-found.component";
import {HomeComponent} from "./home/home.component";
import {CompetitionsDetailsComponent} from "./competitions-details/competitions-details.component";
import {LoginComponent} from "./login/login.component";
import {ProtocolsComponent} from "./protocols/protocols.component";
import {ProtocolsUploadComponent} from "./protocols-upload/protocols-upload.component";
import {ProtocolsDetailsComponent} from "./protocols-details/protocols-details.component";
import {ProtocolsExecutionComponent} from "./protocols-execution/protocols-execution.component";
import {ProtocolDeploymentComponent} from "./protocol-deployment/protocol-deployment.component";
// import {ExecutionComponent} from "./execution/execution.component";

const routes: Routes = [
  {path: '', component:HomeComponent, pathMatch:'full'},
  { path: 'competitions', component:CompetitionsComponent, pathMatch:'full'},
  { path: 'competitions/:name', component:CompetitionsDetailsComponent},
  { path: 'protocols', component:ProtocolsComponent, pathMatch:'full'},
  { path: 'protocols/upload', component:ProtocolsUploadComponent, pathMatch:'full'},
  { path: 'protocols/execution/:name', component: ProtocolsExecutionComponent, pathMatch: 'full'},
  { path: 'protocols/:name', component: ProtocolsDetailsComponent, pathMatch: 'full'},
  { path: 'deployment', component: ProtocolDeploymentComponent, pathMatch: 'full'},
  // { path: 'execution', component: ExecutionComponent, pathMatch: 'full'},
  { path: 'circuits', component:CircuitsComponent, pathMatch:'full'},
  { path: 'login', component:LoginComponent, pathMatch:'full'},
  { path: '**', component:PageNotFoundComponent, pathMatch:'full'},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
export const routingComponents = [
  CompetitionsComponent,
  CircuitsComponent,
  PageNotFoundComponent,
  HomeComponent,
  CompetitionsDetailsComponent
];
