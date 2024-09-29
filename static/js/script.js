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
      if (keyword && keyword!="") {
        url.searchParams.set("keyword", keyword);
        
      }
      else{
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
      }
      window.location.href = url;
    });
  });
}
// price-option
