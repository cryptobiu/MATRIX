import {Component, NgModule, OnInit} from '@angular/core';
import {FormsModule} from "@angular/forms";
import {FormSubmissionService} from "../../Services/formSubmission.service";
import {Router} from "@angular/router";
import {CompetitionRegistration} from "../../classes";

@Component({
  selector: 'app-competitions-registration',
  templateUrl: './competitions-registration.component.html',
  styleUrls: ['./competitions-registration.component.css']
})

@NgModule({
  declarations: [CompetitionsRegistrationComponent],
  imports: [FormsModule],
  exports: [FormsModule]
})

export class CompetitionsRegistrationComponent implements OnInit {

  constructor(private formService:FormSubmissionService, private router: Router) { }

  ngOnInit() {
  }

  submitted = false;
  errmsg = '';
  cr = new CompetitionRegistration('', '');

  onSubmit(){
    this.submitted = true;
    this.formService.submitcompetitionRegistrationForm(this.cr).subscribe(
      data => this.router.navigate(['/competitions']),
      error => this.errmsg = error.statusText
    );
  }

}
