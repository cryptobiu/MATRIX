import { Component, OnInit } from '@angular/core';
import {ActivatedRoute} from "@angular/router";

@Component({
  selector: 'app-competitions-details',
  templateUrl: './competitions-details.component.html',
  styleUrls: ['./competitions-details.component.css']
})
export class CompetitionsDetailsComponent implements OnInit {

  public competitionName;
  constructor(private router: ActivatedRoute) { }

  ngOnInit() {
    let name = this.router.snapshot.paramMap.get('name');
    this.competitionName = name;
  }


}
