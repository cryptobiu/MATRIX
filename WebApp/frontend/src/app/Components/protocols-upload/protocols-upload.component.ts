import {Component, NgModule, OnInit} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {Protocol} from '../../classes';
import {FormSubmissionService} from '../../Services/formSubmission.service';
import {Router} from '@angular/router';

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

  securityLevel = ['Semi Honest', 'Malicious'];
  securityThreshold = ['None', 'Honest Majority', '2/3 Majority'];
  protocolModel = new Protocol('', {}, '', [], 1,
    '', '', '', '', '');
  slHasError = true;
  stHasError = true;
  submitted = false;
  errmsg = '';

  constructor(private _formService: FormSubmissionService, private router: Router) { }

  ngOnInit() {}

  validateSl(value) {
    this.slHasError = value === 'default';
  }

  validateSt(value) {
    this.stHasError = value === 'default';
  }

  onSubmit() {
    this.submitted = true;
    this._formService.submitCreateProtocolForm(this.protocolModel).subscribe(
      data => this.router.navigate(['/protocols']),
      error => this.errmsg = error.statuesText);
  }
}
