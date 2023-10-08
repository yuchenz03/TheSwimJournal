from website import create_app #From the website folder, import the function create app

if __name__ == "__main__": #If we are running this file purely for the content in this file, then
    website = create_app() #creates an app called website
    website.run(debug=True) #When running the app, debugging is always on
  