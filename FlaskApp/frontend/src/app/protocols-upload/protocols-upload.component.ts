import {Component, NgModule, OnInit} from '@angular/core';
import {FormsModule} from "@angular/forms";
import {Protocol} from "../protocol";
import {FormSubmissionService} from "../formSubmission.service";
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
  protocolModel = new Protocol('', '', '', '');
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

  onSubmit(){
    this.submitted = true;
    this._formService.submitForm(this.protocolModel).subscribe(
      data => this.router.navigate(['/protocols']),
      error => this.errmsg = error.statuesText
    )
  }
}
