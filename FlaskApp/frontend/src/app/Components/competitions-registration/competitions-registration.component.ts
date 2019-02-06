import {Component, NgModule, OnInit} from '@angular/core';
import {FormsModule} from "@angular/forms";
import {FormSubmissionService} from "../../Services/formSubmission.service";
import {ActivatedRoute, Router} from "@angular/router";
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

  private competitionName: string;

  constructor(private formService:FormSubmissionService, private router: Router, private acRouter: ActivatedRoute)
  {
    this.competitionName = this.acRouter.snapshot.paramMap.get('name');
  }

  ngOnInit() {
  }

  submitted = false;
  errmsg = '';
  cr = new CompetitionRegistration('', '');

  onSubmit(){
    this.submitted = true;
    this.formService.submitCompetitionRegistrationForm(this.cr, this.competitionName).subscribe(
      data => this.router.navigate(['/competitions']),
      error => this.errmsg = error.statusText
    );
  }

}
