import { Injectable } from '@angular/core';
import {Client} from 'elasticsearch-browser';

@Injectable({
  providedIn: 'root'
})
export class ElasticsearchService {

  constructor(private esClient: Client) {
     this.esClient = new Client({
       host:'https://search-escryptobiu-fyopgg3zepk6dtda4zerc53apy.us-east-1.es.amazonaws.com:9200/',
       log: 'trace',
       use_ssl:true
    });
  }

  getDocuments(): any {
    this.esClient.ping({
      requestTimeout: Infinity,
      body: 'hello JavaSampleApproach!'
    });
    // let requestBody = {
    //   'query': {
    //     'match_all': {}
    //   }
    // };
    // return this.esClient.search({
    //   index:'deployment_matrix_ui',
    //   type: 'deploymentMatrixUI',
    //   body:requestBody,
    //   filterPath: ['hits.hits._source']
    // });
  }
}
