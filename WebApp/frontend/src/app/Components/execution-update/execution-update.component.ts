import { Component, OnInit } from '@angular/core';
import {FormSubmissionService} from '../../Services/formSubmission.service';
import {ActivatedRoute, Router} from '@angular/router';
import {Protocol} from '../../classes';

@Component({
  selector: 'app-execution-update',
  templateUrl: './execution-update.component.html',
  styleUrls: ['./execution-update.component.css']
})
export class ExecutionUpdateComponent implements OnInit {

  submitted = false;
  addressHasError = true;
  errmsg = '';
  private protocolModel: Protocol;

  constructor(private _formService: FormSubmissionService, private router: Router, private acRouter: ActivatedRoute) {
    this.protocolModel.protocolName = this.acRouter.snapshot.paramMap.get('protocolName');
  }

  ngOnInit() {
  }

  onSubmit() {
    this._formService.submitUpdateExecutionForm(this.protocolModel).subscribe(
      data => this.router.navigate(['/execution']),
      error => this.errmsg = error.statuesText);
  }

}
