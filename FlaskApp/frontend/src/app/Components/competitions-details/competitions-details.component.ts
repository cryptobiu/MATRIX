import { Component, OnInit } from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {DbService} from "../../Services/db.service";
// import {ICompetition} from "../../interfaces";
import {Competition} from "../../classes";

@Component({
  selector: 'app-competitions-details',
  templateUrl: './competitions-details.component.html',
  styleUrls: ['./competitions-details.component.css']
})
export class CompetitionsDetailsComponent implements OnInit {

  public competitionName;
  public competition: Competition;
  constructor(private router: ActivatedRoute, private dbService: DbService) { }

  ngOnInit() {
    let competitionName = this.router.snapshot.paramMap.get('name');
    this.dbService.getCompetition(competitionName).subscribe(
      competition => {
        console.log(competition);
        this.competition = new Competition(competition['competitionName'],
        competition['description'],
        competition['startDate'],
        competition['endDate'],
        competition['participants']);
      },
      err => console.log(err)
    );
  }


}
