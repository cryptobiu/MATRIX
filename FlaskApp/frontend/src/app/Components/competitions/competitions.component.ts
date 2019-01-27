import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs/';
import {DataSource} from '@angular/cdk/collections';
import {DbService} from "../../Services/db.service";
import {ICompetition} from "../../interfaces";

@Component({
  selector: 'app-competitions',
  templateUrl: './competitions.component.html',
  styleUrls: ['./competitions.component.css'],
  providers: [DbService]
})

export class CompetitionsComponent implements OnInit {

  dataSource = new CompetitionDataSource(this.dbService);
  displayedColumns = ['competition name', 'description', 'start date', 'end date', 'status', 'registration'];
  constructor(private dbService: DbService) { }

  ngOnInit() {}

}


class CompetitionDataSource extends DataSource<any> {
  constructor(private dbService: DbService) {
    super();
  }

  connect(): Observable<ICompetition[]> {
    return this.dbService.getCompetitions();
  }

  disconnect() {}

}
