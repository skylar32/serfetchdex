/* https://stackoverflow.com/questions/59282842/how-to-make-sorting-html-tables-faster */

function parseCell(cell) {
    if (cell.querySelectorAll("img").length > 0)
        return cell.innerHTML;
    const cellValue = cell.innerText;
    if (cellValue == "—")
        return 0;
    const cellFloat = parseFloat(cellValue)
    if (!isNaN(cellFloat))
        return cellFloat;
    return cellValue;
}

function sortTableRowsByColumn( table, columnIndex, ascending ) {

    const rows = Array.from( table.querySelectorAll( ':scope > tbody > tr' ) );
    
    rows.sort( ( x, y ) => {
        const xValue = parseCell(x.cells[columnIndex]);
        const yValue = parseCell(y.cells[columnIndex]);

        if (ascending) return (xValue > yValue) ? 1 : -1;
        else return (xValue < yValue) ? 1 : -1;
    } );

    for( let row of rows ) {
        table.tBodies[0].appendChild( row );
    }
}

function onColumnHeaderClicked( ev ) {
    
    const th = ev.currentTarget;
    const table = th.closest( 'table' );
    const thIndex = Array.from( th.parentElement.children ).indexOf( th );

    const ascending = !( 'sort' in th.dataset ) || th.dataset.sort != 'asc';
    
    const start = performance.now();

    sortTableRowsByColumn( table, thIndex, ascending );

    const end = performance.now();
    console.log( "Sorted table rows in %d ms.",  end - start );

    const allTh = table.querySelectorAll( ':scope > thead > tr > th' );
    for( let th2 of allTh ) {
        delete th2.dataset['sort'];
    }
 
    th.dataset['sort'] = ascending ? 'asc' : 'desc';
}