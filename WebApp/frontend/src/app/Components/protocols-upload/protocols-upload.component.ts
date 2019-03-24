import {Component, NgModule, OnInit} from '@angular/core';
import {FormsModule} from "@angular/forms";
import {Protocol} from "../../classes";
import {FormSubmissionService} from "../../Services/formSubmission.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-protocols-upload',
  templateUrl: './protocols-upload.component.html',
  styleUrls: ['./protocols-upload.component.css']
})

@NgModule({
  declarations: [ProtocolsUploadComponent],
  imports: [FormsModule],
  exports: [FormsModule]
})

export class ProtocolsUploadComponent implements OnInit {

  constructor(private _formService:FormSubmissionService, private router :Router) { }

  ngOnInit() {
  }

  securityLevel = ['Semi Honest', 'Malicious'];
  securityThreshold = ['None', 'Honest Majority', '2/3 Majority'];
  cloudProvidersName = ['AWS', 'Azure'];
  selectedCP = '';
  awsRegions = ['us-east-1', 'ue-west-2'];
  awsInstances = ['c5.large', 'c5.xlarge', 'c2.2xlarge', 'c5.4xlarge', 'c5.9xlarge', 'c5.18xlarge'];
  azureRegions = ['East US', 'Brazil South'];
  azureInstances = ['Standard_F1s', 'Standard_F2s', 'Standard_F4s', 'Standard_F8s', 'Standard_F16s'];
  regions = [];
  numOfParties = 2;
  instanceType = '';
  gitAddress = '';
  gitBranch = 'master';
  protocolModel = new Protocol('', {}, '', [], 1,
    '', '', '','', '');
  addressHasError = true;
  slHasError = true;
  stHasError = true;
  submitted = false;
  errmsg = '';

  validateAddress(value) {
    if(!value.match(/^https?:\/\//)) this.addressHasError = true;
    else this.addressHasError = false;
  }

  validateSl(value){
    if(value === 'default') this.slHasError = true;
    else this.slHasError = false;
  }

  validateSt(value){
    if(value === 'default') this.stHasError = true;
    else this.stHasError = false;
  }

  onCheckBoxChange(event, value)
  {
    if(event.checked)
      this.regions.push(value);
    if(!event.checked)
    {
      let index = this.regions.indexOf(value)
      if (index >-1)
        this.regions.splice(index, 1);
    }
  }

  onSubmit(){
    this.submitted = true;
    this.protocolModel.cloudProviders[this.selectedCP] = {};
    this.protocolModel.cloudProviders[this.selectedCP]['numOfParties'] = this.numOfParties;
    this.protocolModel.cloudProviders[this.selectedCP]['instanceType'] = this.instanceType;
    this.protocolModel.cloudProviders[this.selectedCP]['regions'] = this.regions;
    this.protocolModel.cloudProviders[this.selectedCP]['git'] = {};
    this.protocolModel.cloudProviders[this.selectedCP]['git']['gitBranch'] = this.gitBranch;
    this.protocolModel.cloudProviders[this.selectedCP]['git']['gitAddress'] = this.gitAddress;
    this._formService.submitUploadProtocolForm(this.protocolModel).subscribe(
      data => this.router.navigate(['/protocols']),
      error => this.errmsg = error.statuesText
    )
  }
}
