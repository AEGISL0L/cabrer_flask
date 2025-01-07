while read package || [ -n "$package" ]; do
    # Skip empty lines and comments
    if [[ ! "$package" =~ ^# ]] && [ -n "$package" ]; then
        echo "Installing $package"
        pip install "$package" || echo "Failed to install $package"
    fi
done < /srv/www/farmacabrer.com/public_html/requirements.txt

