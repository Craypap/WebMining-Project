import {Component} from '@angular/core';
import {MatDialog} from "@angular/material/dialog";
import {NotFoundDialogComponent} from "./not-found-dialog/not-found-dialog.component";
import {RequestService} from "../../service/request.service";

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent {

  recipe: any;
  isSearch: boolean = false;

  constructor(public dialog: MatDialog, private req: RequestService) {}

  search(query: string) {
    //clear error
    this.isSearch = true;
    //search request to AP
    this.req.get_recipe(query).subscribe(
      res => {
        this.isSearch = false;
        this.recipe = res;
      },
      error => {
        this.isSearch = false;
        this.openDialog(query);
      }
    );
    this.isSearch = false;
  }

  canShowRecipe(): boolean {
    return this.recipe != null;
  }

  private openDialog(query: string): void {
    let dialogRef = this.dialog.open(NotFoundDialogComponent, {
      data: {
        query: query,
      }
    });
    dialogRef.disableClose = true
  }
}

