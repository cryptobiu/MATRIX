import {Component, OnInit} from '@angular/core';
import {DbService} from "../db.service";


@Component({
  selector: 'app-competitions',
  templateUrl: './competitions.component.html',
  styleUrls: ['./competitions.component.css'],
  providers: [DbService]
})

export class CompetitionsComponent implements OnInit {

  public competitions = [];
  constructor(private dbService: DbService) { }

  ngOnInit() {
    this.dbService.getCompetitions()
      .subscribe(data => this.competitions = data);
  }

}
