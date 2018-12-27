import { Component, OnInit } from '@angular/core';
import {ActivatedRoute, Router} from "@angular/router";

@Component({
  selector: 'app-competitions-details',
  templateUrl: './competitions-details.component.html',
  styleUrls: ['./competitions-details.component.css']
})
export class CompetitionsDetailsComponent implements OnInit {

  public competitionId;
  constructor(private router: ActivatedRoute) { }

  ngOnInit() {
    let id = parseInt(this.router.snapshot.paramMap.get('id'));
    this.competitionId = id;
  }


}
