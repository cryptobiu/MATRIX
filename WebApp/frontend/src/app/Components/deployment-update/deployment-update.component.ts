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

   awsRegions: Map<string, Array<string>> = new Map([
     ['us-east-1', ['us-east-1a', 'us-east-1b', 'us-east-1c', 'us-east-1d', 'us-east-1e', 'us-east-1f']],
     ['us-east-2', ['us-east-2a', 'us-east-2b', 'us-east-2c']],
     ['us-west-1', ['us-west-1b', 'us-west-1c']],
     ['us-west-2', ['us-west-2a', 'us-west-2b', 'us-west-2c', 'us-west-2d']],
     ['ap-south-1', ['ap-south-1a', 'ap-south-1b', 'ap-south-1c']],
     ['ap-northeast-2', ['ap-northeast-2a', 'ap-northeast-2b', 'ap-northeast-2c']],
     ['ap-southeast-1', ['ap-southeast-1a', 'ap-southeast-1b']],
     ['ap-southeast-2', ['ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c']],
     ['ap-northeast-1', ['ap-northeast-1a', 'ap-northeast-1b', 'ap-northeast-1c']],
     ['ca-central-1', ['ca-central-1a', 'ca-central-1b']],
     ['eu-central-1', ['eu-central-1a', 'eu-central-1b', 'eu-central-1c']],
     ['eu-west-1', ['eu-west-1a', 'eu-west-1b', 'eu-west-1c']],
     ['eu-west-2', ['eu-west-2a', 'eu-west-2b', 'eu-west-2c']],
     ['eu-west-3', ['eu-west-3a', 'eu-west-3b', 'eu-west-3c']],
     ['eu-north-1', ['eu-north-1a', 'eu-north-1b', 'eu-north-1c']],
     ['sa-east-1', ['sa-east-1a', 'sa-east-1b', 'sa-east-1c']]
]);

   selectedZone = ''


  awsArch = ['x86_64', 'ARM'];
  awsX64Instances = ['c5.large', 'c5.xlarge', 'c2.2xlarge', 'c5.4xlarge', 'c5.9xlarge', 'c5.18xlarge'];
  awsArmInstances = ['a1.medium', 'a1.large', 'a1.xlarge', 'a1.2xlarge', 'a1.4xlarge', 'a1.metal'];

  azureRegions = ['Central US', 'East US 2', 'East US', 'North Central US', 'South Central US', 'West US 2',
    'West Central US', 'West US', 'Canada Central', 'Canada East', 'Brazil South', 'North Europe', 'West Europe',
    'France Central', 'France South', 'UK South', 'UK West', 'Germany Central', 'Germany Northeast', 'East Asia',
    'Southeast Asia', 'Australia Central', 'Australia Central 2', 'Australia East', 'Australia Southeast', 'China East',
    'China North', 'China East 2', 'China North 2', 'Central India', 'South India', 'West India', 'Japan East',
    'Japan West', 'Korea Central', 'Korea South', 'South Africa North', 'South Africa West', 'UAE Central', 'UAE North'];
  azureInstances = ['Standard_F1s', 'Standard_F2s', 'Standard_F4s', 'Standard_F8s', 'Standard_F16s'];
  regions = [];
  numOfParties = 2;
  awsSelectedArch = '';
  instanceType = '';
  gitAddress = '';
  gitBranch = 'master';
  submitted = false;
  addressHasError = true;
  errmsg = '';
  private protocolModel: Protocol;

  constructor(private _formService: FormSubmissionService, private router: Router, private acRouter: ActivatedRoute) {
    this.protocolModel.protocolName = this.acRouter.snapshot.paramMap.get('protocolName');
  }

  ngOnInit() {
  }

  validateAddress(value) {
    this.addressHasError = !value.match(/^https?:\/\//);
  }

  isZoneSelected(zone) {
    return this.regions.some(region => region.slice(0, - 1) === zone.slice(0, -1));
  }

  onCheckBoxChange(event, value) {
    const regionSelected = this.isZoneSelected(value);
    if (event.checked && !regionSelected) {
      this.regions.push(value);
    } else {
      const index = this.regions.indexOf(value);
      if (index > -1) {
        this.regions.splice(index, 1);
      }
      if (regionSelected) {
        alert('region already selected, please choose different zone');
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
