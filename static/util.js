var ingredient_count = 1

function add_ingredient() {
    ingredient_count += 1

    var new_html = '<div class="input-group mb-3"><input type="text" class="form-control" placeholder="Ingredient" aria-label="ingredient"><span class="input-group-text">Quantity:<input type="number" class="form-control-sm" aria-label="quantity" id="quantity-label"></span></div>'

    document.getElementById("new_ingredient").innerHTML += new_html

}