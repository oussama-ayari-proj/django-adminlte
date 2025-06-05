document.addEventListener('DOMContentLoaded', function() {
        // Pagination UF
        uf_field_unique_values = document.getElementById('uf-search-field');
        uf_cur_col = uf_field_unique_values.value;
        uf_field = document.getElementById('uf-unique-values-dropdown');
        function attachUfPaginationEvents() {
          document.querySelectorAll('.uf-page-link').forEach(function(link) {
            link.addEventListener('click', function(e) {
              e.preventDefault();
              const page = this.getAttribute('data-page');
              fetch("/ajax_uf_pagination/?page_uf=" + page+ "&field=" + encodeURIComponent(uf_cur_col) + "&value=" + encodeURIComponent(uf_field.value))
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
        sejour_field_unique_values = document.getElementById('sejour-search-field');
        sejour_cur_col = sejour_field_unique_values.value;
        sejour_field = document.getElementById('sejour-unique-values-dropdown');
        function attachSejourPaginationEvents() {
          document.querySelectorAll('.sejour-page-link').forEach(function(link) {
            link.addEventListener('click', function(e) {
              e.preventDefault();
              const page = this.getAttribute('data-page');
              fetch("/ajax_sejours_pagination/?page_sejour=" + page+ "&field=" + encodeURIComponent(sejour_cur_col) + "&value=" + encodeURIComponent(sejour_field.value))
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
        em_field_unique_values = document.getElementById('em-search-field');
        em_cur_col = em_field_unique_values.value;
        em_field = document.getElementById('em-unique-values-dropdown');
        function attachEMPaginationEvents() {
          document.querySelectorAll('.em-page-link').forEach(function(link) {
            link.addEventListener('click', function(e) {
              e.preventDefault();
              const page = this.getAttribute('data-page');
              fetch("/ajax_em_pagination/"+"?page_em=" + page+ "&field=" + encodeURIComponent(em_cur_col) + "&value=" + encodeURIComponent(em_field.value))
                .then(response => response.json())
                .then(data => {
                  document.getElementById('em-table-body').innerHTML = data.table_body;
                  document.getElementById('em-pagination').innerHTML = data.pagination;
                  attachEMPaginationEvents();
                });
            });
          });
        }

        // Pagination for Pole
        pole_field_unique_values = document.getElementById('pole-search-field');
        pole_cur_col = pole_field_unique_values.value;
        pole_field = document.getElementById('pole-unique-values-dropdown');
        function attachPolePaginationEvents() {
          document.querySelectorAll('.pole-page-link').forEach(function(link) {
            link.addEventListener('click', function(e) {
              e.preventDefault();
              const page = this.getAttribute('data-page');
              fetch("/ajax_pole_pagination/?page_pole=" + page+ "&field=" + encodeURIComponent(pole_cur_col) + "&value=" + encodeURIComponent(pole_field.value))
                .then(response => response.json())
                .then(data => {
                  document.getElementById('pole-table-body').innerHTML = data.table_body;
                  document.getElementById('pole-pagination').innerHTML = data.pagination;
                  attachPolePaginationEvents();
                });
            });
          });
        }

        // Pagination for ETB
        etb_field_unique_values = document.getElementById('etb-search-field');
        etb_cur_col = etb_field_unique_values.value;
        etb_field = document.getElementById('etb-unique-values-dropdown');
        function attachEtbPaginationEvents() {
          document.querySelectorAll('.etb-page-link').forEach(function(link) {
            link.addEventListener('click', function(e) {
              e.preventDefault();
              const page = this.getAttribute('data-page');
              fetch("/ajax_etb_pagination/?page_etb=" + page+ "&field=" + encodeURIComponent(etb_cur_col) + "&value=" + encodeURIComponent(etb_field.value))
                .then(response => response.json())
                .then(data => {
                  document.getElementById('etb-table-body').innerHTML = data.table_body;
                  document.getElementById('etb-pagination').innerHTML = data.pagination;
                  attachEtbPaginationEvents();
                });
            });
          });
        }
        // Function calls
        attachUfPaginationEvents();
        attachSejourPaginationEvents();
        attachEMPaginationEvents();
        attachPolePaginationEvents();
        attachEtbPaginationEvents();

        // Unique values for UF search

        function fetchUniqueValues_UF(colName) {
          fetch('/ajax_uf_unique_values/?field=' + encodeURIComponent(colName))
            .then(response => response.json())
            .then(data => {
              const dropdown = document.getElementById('uf-unique-values-dropdown');
              dropdown.innerHTML = '<option value="">-- Valeurs uniques --</option>';
              data.values.forEach(function(val) {
                dropdown.innerHTML += `<option value="${val}">${val}</option>`;
              });
            });
        }
        fetchUniqueValues_UF(uf_cur_col);

        uf_field_unique_values.addEventListener('change', function() {
          uf_cur_col = this.value;
          fetchUniqueValues_UF(uf_cur_col);
        });

        // Unique values for Séjours search
        
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

        // Unique values for Pole search
        function fetchUniqueValues_pole(colName) {
          fetch('/ajax_pole_unique_values/?field=' + encodeURIComponent(colName))
            .then(response => response.json())
            .then(data => {
              const dropdown = document.getElementById('pole-unique-values-dropdown');
              dropdown.innerHTML = '<option value="">-- Valeurs uniques --</option>';
              data.values.forEach(function(val) {
                dropdown.innerHTML += `<option value="${val}">${val}</option>`;
              });
            });
        }
        fetchUniqueValues_pole(pole_cur_col);
        pole_field_unique_values.addEventListener('change', function() {
          pole_cur_col = this.value;
          fetchUniqueValues_pole(pole_cur_col);
        });

        // Unique values for ETB search
        function fetchUniqueValues_etb(colName) {
          fetch('/ajax_etb_unique_values/?field=' + encodeURIComponent(colName))
            .then(response => response.json())
            .then(data => {
              const dropdown = document.getElementById('etb-unique-values-dropdown');
              dropdown.innerHTML = '<option value="">-- Valeurs uniques --</option>';
              data.values.forEach(function(val) {
                dropdown.innerHTML += `<option value="${val}">${val}</option>`;
              });
            });
        }
        fetchUniqueValues_etb(etb_cur_col);
        etb_field_unique_values.addEventListener('change', function() {
          etb_cur_col = this.value;
          fetchUniqueValues_etb(etb_cur_col);
        });

        // Filter and pagination for Séjours
        sejour_field.addEventListener('change', function() {
        const selectedValue = this.value;
        if (selectedValue) {
          fetch('/ajax_sejour_filter/?value=' + encodeURIComponent(selectedValue)+ '&field=' + encodeURIComponent(sejour_cur_col))
            .then(response => response.json())
            .then(data => {
              document.getElementById('sejour-table-body').innerHTML = data.table_body;
              document.getElementById('sejour-pagination').innerHTML = data.pagination;
              attachSejourPaginationEvents();
            });
        } else {
          fetch("/ajax_sejours_pagination/?page_sejour=1")
            .then(response => response.json())
            .then(data => {
              document.getElementById('sejour-table-body').innerHTML = data.table_body;
              document.getElementById('sejour-pagination').innerHTML = data.pagination;
              attachSejourPaginationEvents();
            });
        }
        });
        
        // Filter and pagination for EM
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
          fetch("/ajax_em_pagination/?page_em=1")
            .then(response => response.json())
            .then(data => {
              document.getElementById('em-table-body').innerHTML = data.table_body;
              document.getElementById('em-pagination').innerHTML = data.pagination;
              attachEMPaginationEvents();
            });
        }
        });

        // Filter and pagination for UF
        uf_field.addEventListener('change', function() {
        const selectedValue = this.value;
        if (selectedValue) {
          fetch('/ajax_uf_filter/?value=' + encodeURIComponent(selectedValue)+ '&field=' + encodeURIComponent(uf_cur_col))
            .then(response => response.json())
            .then(data => {
              document.getElementById('uf-table-body').innerHTML = data.table_body;
              document.getElementById('uf-pagination').innerHTML = data.pagination;
              attachUfPaginationEvents();
            });
        } else {
          fetch("/ajax_uf_pagination/?page_uf=1")
            .then(response => response.json())
            .then(data => {
              document.getElementById('uf-table-body').innerHTML = data.table_body;
              document.getElementById('uf-pagination').innerHTML = data.pagination;
              attachUfPaginationEvents();
            });
        }
        });

        // Filter and pagination for Pole
        pole_field.addEventListener('change', function() {
        const selectedValue = this.value;
        if (selectedValue) {
          fetch('/ajax_pole_filter/?value=' + encodeURIComponent(selectedValue)+ '&field=' + encodeURIComponent(pole_cur_col))
            .then(response => response.json())
            .then(data => {
              document.getElementById('pole-table-body').innerHTML = data.table_body;
              document.getElementById('pole-pagination').innerHTML = data.pagination;
              attachPolePaginationEvents();
            });
        } else {
          fetch("/ajax_pole_pagination/?page_pole=1")
            .then(response => response.json())
            .then(data => {
              document.getElementById('pole-table-body').innerHTML = data.table_body;
              document.getElementById('pole-pagination').innerHTML = data.pagination;
              attachPolePaginationEvents();
            });
        }
        });

        // Filter and pagination for ETB
        etb_field.addEventListener('change', function() {
        const selectedValue = this.value;
        if (selectedValue) {
          fetch('/ajax_etb_filter/?value=' + encodeURIComponent(selectedValue)+ '&field=' + encodeURIComponent(etb_cur_col))
            .then(response => response.json())
            .then(data => {
              document.getElementById('etb-table-body').innerHTML = data.table_body;
              document.getElementById('etb-pagination').innerHTML = data.pagination;
              attachEtbPaginationEvents();
            });
        } else {
          fetch("/ajax_etb_pagination/?page_etb=1")
            .then(response => response.json())
            .then(data => {
              document.getElementById('etb-table-body').innerHTML = data.table_body;
              document.getElementById('etb-pagination').innerHTML = data.pagination;
              attachEtbPaginationEvents();
            });
        }
        });

      });

      
      
