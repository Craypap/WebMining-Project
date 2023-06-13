import {Component, Inject} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from "@angular/material/dialog";


export interface DialogData {
  name: string;
  choices: string[];
}

@Component({
  selector: 'app-change-dialog',
  templateUrl: './change-dialog.component.html',
  styleUrls: ['./change-dialog.component.css']
})
export class ChangeDialogComponent {

  choice: string = '';

  /**
   * Constructor of the ChangeDialogComponent. (Dependency injected and auto-assigned)
   * @param dialogRef Reference to the Material Dialog source component
   * @param data Data injected from the component that open the dialog (TournamentComponent)
   */
  constructor(public dialogRef: MatDialogRef<ChangeDialogComponent>, @Inject(MAT_DIALOG_DATA) public data: DialogData) {}

  /**
   * Method to close the dialog
   */
  public closeDialog(updated: boolean): void{
    //get index of choice
    let index = this.data.choices.indexOf(this.choice);
    this.dialogRef.close({updated: updated, newChoice: index})
  }


}
