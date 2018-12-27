import {ICompetition} from "../competition";
// import { CommonModule } from '@angular/common';
import {Component, NgModule, OnInit} from '@angular/core';
import {CompetitionService} from "../competition.service";

// @NgModule({
//   imports: [CommonModule],
//   exports: [],
//   declarations: []
// })

@Component({
  selector: 'app-competitions',
  templateUrl: './competitions.component.html',
  styleUrls: ['./competitions.component.css'],
  providers: [CompetitionService]
})

export class CompetitionsComponent implements OnInit {

  public competitions = [];
  constructor(private _competitionService: CompetitionService) { }

  ngOnInit() {
    this._competitionService.getCompetitions()
      .subscribe(data => this.competitions = data);
  }

}
