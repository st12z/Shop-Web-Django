const csrfToken = document.body.getAttribute("data-csrf-token");
let url = new URL(window.location.href);
//form-search
const formSearch = document.querySelector(".form-search");
if (formSearch) {
  buttonSearch = formSearch.querySelector("#search-addon");
  inputSearch = formSearch.querySelector("input[name='keyword']");
  console.log(buttonSearch);
  if (buttonSearch) {
    buttonSearch.addEventListener("click", () => {
      const keyword = inputSearch.value;
      if (keyword && keyword != "") {
        url.searchParams.set("keyword", keyword);
        url.searchParams.set("page", 1);
      } else {
        url.searchParams.delete("keyword");
      }
      window.location.href = url;
    });
  }
}
//form-search
// pagination
const buttonPagination = document.querySelectorAll(".page-item .page-link");
if (buttonPagination) {
  buttonPagination.forEach((button) => {
    button.addEventListener("click", () => {
      const page = button.getAttribute("data-page");
      url.searchParams.set("page", page);
      window.location.href = url;
    });
  });
}
// pagination

//select-order
const selectOrder = document.querySelector(".select-order");
if (selectOrder) {
  selectOrder.addEventListener("change", (e) => {
    if (e.target.value == "All") {
      url.searchParams.delete("sortKey");
      url.searchParams.delete("sortValue");
      url.searchParams.set("page", 1);
    } else {
      const [sortKey, sortValue] = e.target.value.split("-");
      url.searchParams.set("sortKey", sortKey);
      url.searchParams.set("sortValue", sortValue);
    }
    window.location.href = url;
  });
}
//select-order

// price-option
const radioPrice = document.querySelectorAll("input[name='price']");
if (radioPrice) {
  radioPrice.forEach((radio) => {
    radio.addEventListener("click", (e) => {
      const priceOrder = e.target.value;
      console.log(priceOrder);
      if (priceOrder == "") {
        url.searchParams.delete("priceOrder");
      } else {
        url.searchParams.set("priceOrder", priceOrder);
        url.searchParams.set("page", 1);
      }
      window.location.href = url;
    });
  });
}
// price-option

// category
const buttonCategory = document.querySelectorAll("[button-category]");
if (buttonCategory) {
  buttonCategory.forEach((button) => {
    button.addEventListener("click", () => {
      const category = button.getAttribute("button-category");
      url.searchParams.set("category", category);
      url.searchParams.set("page", 1);
      url.searchParams.delete("keyword");
      window.location.href = url;
    });
  });
}
// end category


// Add product to Cart
const quantityCart = document.querySelector("[quantity-cart]");
const buttonAddCart = document.querySelectorAll("[button-add-cart]");
console.log(quantityCart);
if (buttonAddCart) {
  buttonAddCart.forEach((button) => {
    button.addEventListener("click", () => {
      const productId = button.getAttribute("productId");
      fetch(`http://127.0.0.1:8000/home/add-cart/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          productId: productId,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
          if (quantityCart) quantityCart.innerHTML = `(${data.total_quantity})`;
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    });
  });
}
// end

// Decrease Cart
const buttonProcess = document.querySelectorAll("[button-process]");
const tableCart = document.querySelector(".table-cart");
const totalPayment=document.querySelector("[total-payment]");

if (buttonProcess) {
  buttonProcess.forEach((button) => {
    button.addEventListener("click", () => {
      const typeProcess = button.getAttribute("type-process");
      const productId = button.getAttribute("product-id");
      const record = tableCart.querySelector(`tr[record='${productId}']`);
      const totalPrice=tableCart.querySelector(`[total-price='${productId}']`);
      console.log(totalPrice);
      console.log(totalPayment);
      const inputQuantityCart = document.querySelector(
        `input[quantity-cart-input='${productId}']`
      );
      fetch(`http://127.0.0.1:8000/home/${typeProcess}-product/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          productId: productId,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log(data);
          if (inputQuantityCart) {
            inputQuantityCart.value = data.quantity;
            quantityCart.innerHTML = `(${data.total_quantity})`;
            totalPrice.innerHTML=data.total_price +"VNĐ",
            totalPayment.innerHTML=`Tổng tiền thanh toán : ${data.total_payment} VNĐ`
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    });
  });
}
// End Decrease cart

// button-alert
const buttonAlert=document.querySelector("[close-alert]");
if(buttonAlert){
  buttonAlert.addEventListener("click",()=>{
    const notify=document.querySelector("[alert-message]");
    notify.classList.add("hidden");
  })
}

// end button-alert

// button-cancel-order

// end-button-cancel-order
