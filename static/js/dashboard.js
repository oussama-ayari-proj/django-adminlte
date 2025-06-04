document.addEventListener('DOMContentLoaded', function() {
        // Pagination UF
        function attachUfPaginationEvents() {
          document.querySelectorAll('.uf-page-link').forEach(function(link) {
            link.addEventListener('click', function(e) {
              e.preventDefault();
              const page = this.getAttribute('data-page');
              fetch("{% url 'ajax_uf_pagination' %}?page_uf=" + page)
                .then(response => response.json())
                .then(data => {
                  document.getElementById('uf-table-body').innerHTML = data.table_body;
                  document.getElementById('uf-pagination').innerHTML = data.pagination;
                  attachUfPaginationEvents();
                });
            });
          });
        }
        // Pagination Sejour
        function attachSejourPaginationEvents() {
          document.querySelectorAll('.sejour-page-link').forEach(function(link) {
            link.addEventListener('click', function(e) {
              e.preventDefault();
              const page = this.getAttribute('data-page');
              fetch("{% url 'ajax_sejours_pagination' %}?page_sejour=" + page+ "&field=" + encodeURIComponent(sejour_cur_col) + "&value=" + encodeURIComponent(sejour_field_unique_values.value))
                .then(response => response.json())
                .then(data => {
                  document.getElementById('sejour-table-body').innerHTML = data.table_body;
                  document.getElementById('sejour-pagination').innerHTML = data.pagination;
                  attachSejourPaginationEvents();
                });
            });
          });
        }
        
        // Pagination for EM
        function attachEMPaginationEvents() {
          document.querySelectorAll('.em-page-link').forEach(function(link) {
            link.addEventListener('click', function(e) {
              e.preventDefault();
              const page = this.getAttribute('data-page');
              console.log("Fetching EM page:", page);
              fetch("{% url 'ajax_em_pagination' %}?page_em=" + page+ "&field=" + encodeURIComponent(em_cur_col) + "&value=" + encodeURIComponent(em_field.value))
                .then(response => response.json())
                .then(data => {
                  document.getElementById('em-table-body').innerHTML = data.table_body;
                  document.getElementById('em-pagination').innerHTML = data.pagination;
                  attachEMPaginationEvents();
                });
            });
          });
        }
        // Function calls
        attachUfPaginationEvents();
        attachSejourPaginationEvents();
        attachEMPaginationEvents();

        // Unique values for UF search
        uf_field_unique_values = document.getElementById('uf-search-field');
        uf_cur_col = uf_field_unique_values.value;

        function fetchUfUniqueValues(colName) {
          fetch('/ajax_uf_unique_values/?field=' + encodeURIComponent(colName))
            .then(response => response.json())
            .then(data => {
              const dropdown = document.getElementById('unique-values-dropdown');
              dropdown.innerHTML = '<option value="">-- Valeurs uniques --</option>';
              data.values.forEach(function(val) {
                dropdown.innerHTML += `<option value="${val}">${val}</option>`;
              });
            });
        }
        fetchUfUniqueValues(uf_cur_col);

        uf_field_unique_values.addEventListener('change', function() {
          uf_cur_col = this.value;
          fetchUfUniqueValues(uf_cur_col);
        });

        // Unique values for Séjours search
        sejour_field_unique_values = document.getElementById('sejour-search-field');
        sejour_cur_col = sejour_field_unique_values.value;
        console.log(sejour_cur_col);

        function fetchUniqueValues_sejour(colName) {
          fetch('/ajax_sejour_unique_values/?field=' + encodeURIComponent(colName))
            .then(response => response.json())
            .then(data => {
              const dropdown = document.getElementById('sejour-unique-values-dropdown');
              dropdown.innerHTML = '<option value="">-- Valeurs uniques --</option>';
              data.values.forEach(function(val) {
                dropdown.innerHTML += `<option value="${val}">${val}</option>`;
              });
            });
        }
        fetchUniqueValues_sejour(sejour_cur_col);

        sejour_field_unique_values.addEventListener('change', function() {
          sejour_cur_col = this.value;
          fetchUniqueValues_sejour(sejour_cur_col);
        });

        // Unique values for EM search
        em_field_unique_values = document.getElementById('em-search-field');
        em_cur_col = em_field_unique_values.value;
        function fetchUniqueValues_em(colName) {
          fetch('/ajax_em_unique_values/?field=' + encodeURIComponent(colName))
            .then(response => response.json())
            .then(data => {
              const dropdown = document.getElementById('em-unique-values-dropdown');
              dropdown.innerHTML = '<option value="">-- Valeurs uniques --</option>';
              data.values.forEach(function(val) {
                dropdown.innerHTML += `<option value="${val}">${val}</option>`;
              });
            });
        }
        fetchUniqueValues_em(em_cur_col);
        em_field_unique_values.addEventListener('change', function() {
          em_cur_col = this.value;
          fetchUniqueValues_em(em_cur_col);
        });

      });

      em_field = document.getElementById('em-unique-values-dropdown');
      em_field.addEventListener('change', function() {
        const selectedValue = this.value;
        if (selectedValue) {
          fetch('/ajax_em_filter/?value=' + encodeURIComponent(selectedValue)+ '&field=' + encodeURIComponent(em_cur_col))
            .then(response => response.json())
            .then(data => {
              document.getElementById('em-table-body').innerHTML = data.table_body;
              document.getElementById('em-pagination').innerHTML = data.pagination;
              attachEMPaginationEvents();
            });
        } else {
          // If no value is selected, reload the full table
          fetch(window.ajaxEmPaginationUrl + "?page_em=1")
            .then(response => response.json())
            .then(data => {
              document.getElementById('em-table-body').innerHTML = data.table_body;
              document.getElementById('em-pagination').innerHTML = data.pagination;
            });
        }
      });
