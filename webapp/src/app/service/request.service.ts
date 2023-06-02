import { Injectable } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {Observable} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class RequestService {

  baseUrl = "http://127.0.0.1:8000"; //URL to the API

  /**
   * Constructor of the RequestService (Dependency injected and auto-assigned)
   * (It changes to baseURL to localhost in case we run the app in dev mode...)
   * @param http HTTP client to use for doing all HTTP requests
   */
  constructor(private http: HttpClient) {}

  //=======================================================
  // GET
  //=======================================================

  /**
   * Do the request to get the recipe
   */
  get_recipe(query: string): Observable<any> {
    return this.http.get<any>(this.baseUrl + "/recipe/"+query)
  }

  /**
   * Do the request to get the last actuation date
   */
  get_date(): Observable<any> {
    return this.http.get<any>(this.baseUrl + "/date")
  }
}
