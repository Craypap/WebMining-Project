import {Component, EventEmitter, Input, OnChanges, OnDestroy, OnInit, Output, SimpleChanges} from '@angular/core';
import {MatDialog} from "@angular/material/dialog";
import {ChangeDialogComponent} from "./change-dialog/change-dialog.component";

@Component({
  selector: 'app-recipe',
  templateUrl: './recipe.component.html',
  styleUrls: ['./recipe.component.css']
})
export class RecipeComponent implements OnChanges, OnInit, OnDestroy{

  @Input() recipe: any = {}
  @Output() clearRecipe = new EventEmitter()
  protected readonly window = window;

  sliderValue: number = 1;
  sliderMax: number = 2;
  total: number = 0.0; //total price of the recipe at Aldi

  changesInterval: any;
  oldSliderValue: number = this.sliderValue;

  constructor(public dialog: MatDialog) {}

  ngOnChanges(changes: SimpleChanges): void {
    if(changes.hasOwnProperty('recipe')){
      this.sliderValue = this.recipe.servings_quantity;
      this.sliderMax = this.recipe.servings_quantity * 2;
      this.applyServingsChange();
      console.log(this.recipe)
    }
  }

  ngOnInit(): void {
    this.changesInterval = setInterval(() => {
      if(this.sliderValue != this.oldSliderValue){
        // apply changes
        this.applyServingsChange();
        this.oldSliderValue = this.sliderValue;
      }
    }, 1000);
  }

  ngOnDestroy(): void {
    clearInterval(this.changesInterval);
  }

  computeNumberOfPieces(ingredient: any): number{
    // check if invariant, return 1
    if(ingredient.quantity_kg == 0) return 1;
    return Math.ceil(ingredient.quantity_kg / parseFloat(ingredient.match.quantity));
  }

  updateQuantityString(quantity: string, factor: number): string{
    quantity = quantity.toLowerCase();
    quantity = quantity.trim();
    if(quantity == '') return '';
    let tmp = quantity.split(' ', 2);
    // check if quantity is a fraction
    if(tmp[0].includes('/')){
      let frac = tmp[0].split('/');
      let num = parseFloat(frac[0]);
      let den = parseFloat(frac[1]);
      tmp[0] = (num/den).toString();
    }
    //check if quantity is a number
    let t = (parseFloat(tmp[0]) * factor).toFixed(2);
    if (parseFloat(t)%1 == 0) t = parseInt(t).toString();
    if (tmp.length == 1)return t
    return t + ' ' + tmp[1];
  }

  computeTotalPrice(): void{
    this.total = 0.0;
    for(let ingredient of this.recipe.ingredients){
      this.total += ingredient.match.price * this.computeNumberOfPieces(ingredient);
    }
    this.total = parseFloat(this.total.toFixed(2));
  }

  applyServingsChange(): void{
    for(let ingredient of this.recipe.ingredients){
      ingredient.quantity = this.updateQuantityString(ingredient.quantity, this.sliderValue/this.recipe.servings_quantity);
      ingredient.quantity_kg = (ingredient.quantity_kg/this.recipe.servings_quantity) * this.sliderValue;
    }
    this.recipe.servings_quantity = this.sliderValue;
    // compute total price
    this.computeTotalPrice();
  }

  openChangeDialog(name: string, others: any[]): void{
    // create a list of choices
    let choices = [];
    for(let other of others){
      choices.push(other.name);
    }
    let dialogRef = this.dialog.open(ChangeDialogComponent, {
      data: {
        name: name,
        choices: choices
      }
    });
    dialogRef.disableClose = true
    dialogRef.afterClosed().subscribe(
      res => {
        if(res.updated){
          //update match by the new choice
          for(let i of this.recipe.ingredients){
            if(i.name == name){
              i.match = others[res.newChoice];
              // trigger price update
              this.applyServingsChange();
              break;
            }
          }
        }
      }
    )

  }


}
