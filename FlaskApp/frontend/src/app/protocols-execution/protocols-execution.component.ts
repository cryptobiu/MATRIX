import { Component, OnInit } from '@angular/core';
import {DbService} from "../db.service";

@Component({
  selector: 'app-protocols-execution',
  templateUrl: './protocols-execution.component.html',
  styleUrls: ['./protocols-execution.component.css']
})
export class ProtocolsExecutionComponent implements OnInit {

  private fileData: string[];

  constructor(private dbService: DbService) { }

  ngOnInit() {
    this.readData();
  }

  readData(){
    this.dbService.readTextFile().
    subscribe(data => this.fileData = data.split('\n'));
    return this.fileData;
  }

}
