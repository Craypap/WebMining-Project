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
  lastActuation: string = "-";

  constructor(public dialog: MatDialog, private req: RequestService) {
    this.getLatestActuation();
  }

  search(query: string) {
    //clear error
    this.isSearch = true;
    //search request to AP
    this.req.get_recipe(query).subscribe(
      res => {
        this.isSearch = false;
        this.recipe = res;
        console.log(this.recipe)
      },
      error => {
        this.isSearch = false;
        this.openDialog(query);
      }
    );
    this.isSearch = false;
  }

  private getLatestActuation() {
    this.req.get_date().subscribe(
      res => {
        this.lastActuation = res.last_action_date;
      }
    );
  }

  canShowRecipe(): boolean {
    return this.recipe != null;
  }

  clearRecipe() {
    this.recipe = null;
  }

  private openDialog(query: string): void {
    let dialogRef = this.dialog.open(NotFoundDialogComponent, {
      data: {
        query: query,
      }
    });
    dialogRef.disableClose = true;
  }

  scrape(){
    this.req.scrape().subscribe(
      res => {
        alert("Données Actualisées !")
      }
    );
  }
}

