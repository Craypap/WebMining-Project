import {Component} from '@angular/core';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent {

  recipe: any;
  isSearch: boolean = false;

  constructor() {
  }

  search(query: string) {
    this.isSearch = true;
    //TODO: search request to API
  }

  canShowRecipe(): boolean {
    return this.recipe != null;
  }
}

