import {Component, OnInit} from '@angular/core';
import {DbService} from '../../Services/db.service';
import {ActivatedRoute, Router} from '@angular/router';
import {Protocol} from '../../classes';

@Component({
  selector: 'app-deployment-configuration',
  templateUrl: './deployment-configuration.component.html',
  styleUrls: ['./deployment-configuration.component.css']
})
export class DeploymentConfigurationComponent implements OnInit {
  public protocolModel: Protocol;
  public selectedCP: string;
  public numberOfParties: number;
  public instanceType: string;
  public gitAddress: string;
  public gitBranch: string;

  constructor(private dbService: DbService, private router: Router, private acRouter: ActivatedRoute) {
    const protocolName = this.acRouter.snapshot.paramMap.get('protocolName');

    this.dbService.getProtocol(protocolName).
    subscribe(val => {
      this.protocolModel = new Protocol(val);
      this.selectedCP = Object.keys(this.protocolModel.cloudProviders)[0];
      this.numberOfParties = this.protocolModel.cloudProviders[this.selectedCP].numOfParties;
      this.instanceType = this.protocolModel.cloudProviders[this.selectedCP].instanceType;
      this.gitAddress = this.protocolModel.cloudProviders[this.selectedCP]['git'].gitAddress;
      this.gitBranch = this.protocolModel.cloudProviders[this.selectedCP]['git'].gitBranch;
    }, error => console.error(error));
  }

  ngOnInit() {
    this.protocolModel = new Protocol();
  }

}
