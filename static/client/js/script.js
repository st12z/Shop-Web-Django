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
      if (category != "") url.searchParams.set("category", category);
      else {
        url.searchParams.delete("category");
      }
      url.searchParams.set("page", 1);
      url.searchParams.delete("keyword");
      window.location.href = url;
    });
  });
}
// end category
const closeAlert=()=>{
  const buttonAlert = document.querySelector("[close-alert]");
  if (buttonAlert) {
    buttonAlert.addEventListener("click", () => {
      
      const notify = document.querySelector("[alert-message]");
      console.log(buttonAlert);
      console.log(notify);
      notify.classList.add("hidden");

    });
  }
}
// Add product to Cart
const body=document.querySelector("body");
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
          if (quantityCart){
            quantityCart.innerHTML = `(${data.total_quantity})`;
            if(data.messages){
              const alertMess=document.querySelector("[alert-message]");
              if(alertMess){
                body.removeChild(alertMess);
              }
              const spanMess=document.createElement("span");
              spanMess.classList.add("alert");
              spanMess.setAttribute("alert-message","");
              spanMess.classList.add("alert-danger");
              spanMess.innerHTML=`${data.messages} <span close-alert>X</span>`;
              body.appendChild(spanMess);
              closeAlert();
            }
          }
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
const tableCart = document.querySelector("[table-cart]");
console.log(tableCart);
const totalPayment = document.querySelector("[total-payment]");

if (buttonProcess) {
  buttonProcess.forEach((button) => {
    button.addEventListener("click", () => {
      const typeProcess = button.getAttribute("type-process");
      const productId = button.getAttribute("product-id");
      const totalPrice = tableCart.querySelector(
        `[total-price='${productId}']`
      );
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
            (totalPrice.innerHTML = data.total_price + "VNĐ"),
              (totalPayment.innerHTML = `Tổng tiền thanh toán : ${data.total_payment} VNĐ`);
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

closeAlert();


// end button-alert

// button-cancel-order
const buttonCancel = document.querySelectorAll("[button-cancel]");
if (buttonCancel) {
  buttonCancel.forEach((button) => {
    button.addEventListener("click", () => {
      const orderId = button.getAttribute("button-cancel");
      const buttonOrder = document.querySelector(`[button-order="${orderId}"]`);
      console.log(orderId);
      fetch(`http://127.0.0.1:8000/home/cancel-order/${orderId}/`, {
        method: "DELETE",
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.code == 200) {
            if (buttonCancel) {
              button.innerHTML = "Đã hủy đơn hàng";
              if (buttonOrder) buttonOrder.remove();
              button.setAttribute("disabled", true);
            }
          }
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    });
  });
}

// end-button-cancel-order
const inputUpload = document.querySelector("#imageUpload");
if (inputUpload) {
  const imgUpload = document.querySelector("#image-preview");

  inputUpload.addEventListener("change", (e) => {
    // Kiểm tra xem có file nào được chọn
    if (e.target.files && e.target.files[0]) {
      imgUpload.src = URL.createObjectURL(e.target.files[0]);
      console.log(imgUpload.src);
      imgUpload.style.display = "block"; // Hiển thị ảnh sau khi chọn
    }
  });
}