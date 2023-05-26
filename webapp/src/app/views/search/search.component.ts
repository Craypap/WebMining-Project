import {Component} from '@angular/core';
import {MatDialog} from "@angular/material/dialog";
import {NotFoundDialogComponent} from "./not-found-dialog/not-found-dialog.component";

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent {

  recipe: any;
  isSearch: boolean = false;
  notFoundMessage: string = "";

  constructor(public dialog: MatDialog) {
  }

  search(query: string) {
    //clear error
    this.notFoundMessage = "";
    this.isSearch = true;
    //TODO: search request to AP
    this.isSearch = false;
    let dialogRef = this.dialog.open(NotFoundDialogComponent, {
      data: {
        query: query,
      }
    });
    dialogRef.disableClose = true
  }

  canShowRecipe(): boolean {
    return this.recipe != null;
  }
}

