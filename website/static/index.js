function deleteExpense(expenseId) {
    fetch('/delete-expense',{
        method: 'POST',
        body: JSON.stringify({ expenseId: expenseId}),
    }).then((_res) => {
        window.location.href = "/expenses";
    });
}

function deleteIncome(incomeId) {
    fetch('/delete-income',{
        method: 'POST',
        body: JSON.stringify({ incomeId: incomeId}),
    }).then((_res) => {
        window.location.href = "/incomes";
    });
}

function deleteEtag(etagId) {
    fetch('/delete-etag',{
        method: 'POST',
        body: JSON.stringify({ etagId: etagId}),
    }).then((_res) => {
        window.location.href = "/etags";
    });
}

function deleteItag(itagId) {
    fetch('/delete-itag',{
        method: 'POST',
        body: JSON.stringify({ itagId: itagId}),
    }).then((_res) => {
        window.location.href = "/itags";
    });
}

function deleteSaving(savingId) {
    fetch('/delete-saving',{
        method: 'POST',
        body: JSON.stringify({ savingId: savingId}),
    }).then((_res) => {
        window.location.href = "/savings";
    });
}

function deleteNote(noteId) {
    fetch('/delete-note',{
        method: 'POST',
        body: JSON.stringify({ noteId: noteId}),
    }).then((_res) => {
        window.location.href = "/";
    });
}

