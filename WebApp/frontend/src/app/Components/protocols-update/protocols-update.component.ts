import { Component, OnInit } from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Protocol} from '../../classes';
import {DbService} from '../../Services/db.service';
import {FormSubmissionService} from '../../Services/formSubmission.service';
import {take} from 'rxjs/operators';

@Component({
  selector: 'app-protocols-update',
  templateUrl: './protocols-update.component.html',
  styleUrls: ['./protocols-update.component.css']
})
export class ProtocolsUpdateComponent implements OnInit {

  private protocolModel: Protocol;
  securityLevel = ['Semi Honest', 'Malicious'];
  securityThreshold = ['None', 'Honest Majority', '2/3 Majority'];
  slHasError = true;
  stHasError = true;
  submitted = false;
  errmsg = '';

  constructor(private _formService: FormSubmissionService, private dbService: DbService,
              private router: Router, private acRouter: ActivatedRoute) {

    const protocolName = this.acRouter.snapshot.paramMap.get('protocolName');

    this.dbService.getProtocol(protocolName).
    subscribe(val => {
      this.protocolModel = new Protocol(val);
    }, error => error);
  }

  ngOnInit() {
    this.protocolModel = new Protocol();
  }

   validateSl(value) {
    this.slHasError = value === 'default';
  }

  validateSt(value) {
    this.stHasError = value === 'default';
  }

  onSubmit() {
    this._formService.submitUpdateProtocolForm(this.protocolModel).subscribe(
      data => this.router.navigate(['/protocols']),
      error => this.errmsg = error.statuesText);
  }

}
