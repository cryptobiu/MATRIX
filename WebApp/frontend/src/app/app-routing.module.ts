import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {CompetitionsComponent} from "./Components/competitions/competitions.component";
import {CircuitsComponent} from "./Components/circuits/circuits.component";
import {PageNotFoundComponent} from "./Components/page-not-found/page-not-found.component";
import {HomeComponent} from "./Components/home/home.component";
import {CompetitionsDetailsComponent} from "./Components/competitions-details/competitions-details.component";
import {LoginComponent} from "./Components/login/login.component";
import {ProtocolsComponent} from "./Components/protocols/protocols.component";
import {ProtocolsUploadComponent} from "./Components/protocols-upload/protocols-upload.component";
import {DeploymentComponent} from "./Components/deployment/deployment.component";
import {ExecutionComponent} from "./Components/execution/execution.component";
import {DeploymentResultComponent} from "./Components/deployment-result/deployment-result.component";
import {ReportingComponent} from "./Components/reporting/reporting.component";
import {ExecutionResultComponent} from "./Components/execution-result/execution-result.component";
import {CompetitionsRegistrationComponent} from "./Components/competitions-registration/competitions-registration.component";
import {ReportingResultComponent} from "./Components/reporting-result/reporting-result.component";
import {CallbackComponent} from "./Components/callback/callback.component";

const routes: Routes = [
  { path: '', component:HomeComponent, pathMatch:'full'},
  { path: 'competitions', component:CompetitionsComponent, pathMatch:'full'},
  { path: 'competitions/:name', component:CompetitionsDetailsComponent},
  { path: 'competitions/registration/:name', component:CompetitionsRegistrationComponent},
  { path: 'protocols', component:ProtocolsComponent, pathMatch:'full'},
  { path: 'protocols/upload', component:ProtocolsUploadComponent, pathMatch:'full'},
  { path: 'deployment', component: DeploymentComponent, pathMatch: 'full'},
  { path: 'deployment/:protocolName/:action', component: DeploymentResultComponent, pathMatch: 'full'},
  { path: 'execution', component: ExecutionComponent, pathMatch: 'full'},
  { path: 'execution/:protocolName/:action', component: ExecutionResultComponent, pathMatch: 'full'},
  { path: 'reporting', component: ReportingComponent, pathMatch: 'full'},
  { path: 'reporting/:protocolName/:action', component: ReportingResultComponent, pathMatch: 'full'},
  { path: 'circuits', component:CircuitsComponent, pathMatch:'full'},
  { path: 'login', component:LoginComponent, pathMatch:'full'},
  { path: 'callback', component:CallbackComponent, pathMatch:'full'},
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
