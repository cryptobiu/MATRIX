import { Component, OnInit } from '@angular/core';
import {FormSubmissionService} from '../../Services/formSubmission.service';
import {ActivatedRoute, Router} from '@angular/router';
import {Protocol} from '../../classes';

@Component({
  selector: 'app-deployment-update',
  templateUrl: './deployment-update.component.html',
  styleUrls: ['./deployment-update.component.css']
})
export class DeploymentUpdateComponent implements OnInit {

  cloudProvidersName = ['AWS', 'Azure'];
  selectedCP = '';
  awsRegions = ['us-east-2', 'us-east-1', 'us-west-1', 'us-west-2', 'ap-east-1', 'ap-south-1', 'ap-northeast-3',
    'ap-northeast-2', 'ap-southeast-1', 'ap-southeast-1', 'ap-northeast-1', 'ca-central-1', 'eu-central-1',
    'eu-west-1', 'eu-west-2', 'ue-west-3', 'eu-north-1', 'sa-east-1 '];
  awsInstances = ['c5.large', 'c5.xlarge', 'c2.2xlarge', 'c5.4xlarge', 'c5.9xlarge', 'c5.18xlarge'];

  azureRegions = ['Central US', 'East US 2', 'East US', 'North Central US', 'South Central US', 'West US 2',
    'West Central US', 'West US', 'Canada Central', 'Canada East', 'Brazil South', 'North Europe', 'West Europe',
    'France Central', 'France South', 'UK South', 'UK West', 'Germany Central', 'Germany Northeast', 'East Asia',
    'Southeast Asia', 'Australia Central', 'Australia Central 2', 'Australia East', 'Australia Southeast', 'China East',
    'China North', 'China East 2', 'China North 2', 'Central India', 'South India', 'West India', 'Japan East',
    'Japan West', 'Korea Central', 'Korea South', 'South Africa North', 'South Africa West', 'UAE Central', 'UAE North'];
  azureInstances = ['Standard_F1s', 'Standard_F2s', 'Standard_F4s', 'Standard_F8s', 'Standard_F16s'];
  regions = [];
  numOfParties = 2;
  instanceType = '';
  gitAddress = '';
  gitBranch = 'master';
  submitted = false;
  addressHasError = true;
  errmsg = '';
  protocolModel = new Protocol('', {}, '', [], 1,
    '', '', '', '', '');

  constructor(private _formService: FormSubmissionService, private router: Router, private acRouter: ActivatedRoute) {
    this.protocolModel.protocolName = this.acRouter.snapshot.paramMap.get('protocolName');
  }

  ngOnInit() {
  }

  validateAddress(value) {
    this.addressHasError = !value.match(/^https?:\/\//);
  }

  onCheckBoxChange(event, value) {
    if (event.checked) {
      this.regions.push(value);
    } else {
      const index = this.regions.indexOf(value);
      if (index > -1) {
        this.regions.splice(index, 1);
      }
    }
  }

  onSubmit() {
    this.submitted = true;
    this.protocolModel.cloudProviders[this.selectedCP] = {};
    this.protocolModel.cloudProviders[this.selectedCP]['numOfParties'] = this.numOfParties;
    this.protocolModel.cloudProviders[this.selectedCP]['instanceType'] = this.instanceType;
    this.protocolModel.cloudProviders[this.selectedCP]['regions'] = this.regions;
    this.protocolModel.cloudProviders[this.selectedCP]['git'] = {};
    this.protocolModel.cloudProviders[this.selectedCP]['git']['gitBranch'] = this.gitBranch;
    this.protocolModel.cloudProviders[this.selectedCP]['git']['gitAddress'] = this.gitAddress;
    this._formService.submitUpdateDeployForm(this.protocolModel).subscribe(
      data => this.router.navigate(['/deployment']),
      error => this.errmsg = error.statuesText);
  }

}
