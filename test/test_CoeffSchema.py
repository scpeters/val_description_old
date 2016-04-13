#!/usr/bin/env python

import unittest
import glob
import os
import CoeffSchemaDefinitions as coeffSchemaDefinitions
import CoeffCollectionDefinitions as coeffCollectionDefinitions
from lxml import etree as xmlParser
import lxml
import logging

classToActuatorCoeffFilenameDictionary = {'a': 'v_a_', 'b': 'v_b_', 'c': 'v_c_', 'd': 'v_d_', 'e': 'v_e_', 'f': 'v_f_', 'g': 'v_g_', 'h_athena1': 'athena1', 'h_athena2': 'athena2'}

classToActuatorSchemaDictionary = {'a': coeffSchemaDefinitions.actuator_coeffs_definition,
                                   'b': coeffSchemaDefinitions.actuator_coeffs_definition,
                                   'c': coeffSchemaDefinitions.actuator_coeffs_definition,
                                   'd': coeffSchemaDefinitions.actuator_coeffs_definition,
                                   'e': coeffSchemaDefinitions.actuator_coeffs_definition,
                                   'f': coeffSchemaDefinitions.actuator_coeffs_definition,
                                   'g': coeffSchemaDefinitions.actuator_coeffs_definition,
                                   'h_athena1': coeffSchemaDefinitions.athena1_actuator_coeffs_definition,
                                   'h_athena2': coeffSchemaDefinitions.athena2_actuator_coeffs_definition}

classToActuatorCoeffFilesSchemaDictionary = {'a': coeffSchemaDefinitions.actuator_coeff_files_definition,
                                             'b': coeffSchemaDefinitions.actuator_coeff_files_definition,
                                             'c': coeffSchemaDefinitions.actuator_coeff_files_definition,
                                             'd': coeffSchemaDefinitions.actuator_coeff_files_definition,
                                             'e': coeffSchemaDefinitions.actuator_coeff_files_definition,
                                             'f': coeffSchemaDefinitions.actuator_coeff_files_definition,
                                             'g': coeffSchemaDefinitions.actuator_coeff_files_definition,
                                             'h_athena1': ''' ''',
                                             'h_athena2': ''' '''}


class coeffFileTests(unittest.TestCase):

    def setUp(self):
        self.catkinWorkspaceDirectory = os.getenv("VAL_WORKSPACE")

        # Define the directories that coeffs live in
        self.actuatorCoeffDirectory = self.catkinWorkspaceDirectory + '/src/val_description/instance/coefficients/actuators'
        self.classCoeffDirectory = self.catkinWorkspaceDirectory + '/src/val_description/instance/coefficients/class'
        self.controllerCoeffDirectory = self.catkinWorkspaceDirectory + '/src/val_description/instance/coefficients/controllers'
        self.locationCoeffDirectory = self.catkinWorkspaceDirectory + '/src/val_description/instance/coefficients/location'
        self.modesCoeffDirectory = self.catkinWorkspaceDirectory + '/src/val_description/instance/coefficients/modes'
        self.safetyCoeffDirectory = self.catkinWorkspaceDirectory + '/src/val_description/instance/coefficients/safety'
        self.sensorCoeffDirectory = self.catkinWorkspaceDirectory + '/src/val_description/instance/coefficients/sensors'

        self.log = logging.getLogger("Coeff Test Logger")
        self.correctFiles = []
        self.incorrectFiles = []

    def tearDown(self):
        pass

    def getSchemaParser(self, schema_definition):
        schema_root = xmlParser.XML(schema_definition)
        schema = xmlParser.XMLSchema(schema_root)
        return xmlParser.XMLParser(schema=schema)

    def checkForDuplicates(self, directory):
        # Assemble the schema
        os.chdir(directory)
        for coeffFile in glob.glob("*.xml"):
            try:
                xmlCoeffObject = xmlParser.parse(coeffFile)
                coeffNames = []
                for coeff in xmlCoeffObject.iter('Coeff'):
                    coeffNames.append(coeff.get('id'))
                if len(coeffNames) != len(set(coeffNames)):
                    raise Exception
            except Exception:
                self.log.error(coeffFile + " has duplicate coeffs")
                self.incorrectFiles.append(coeffFile)
        assert len(self.incorrectFiles) == 0

    def checkForNeeded(self, directory, classToCheck, neededCoeffs, filenameString):
        os.chdir(directory)

        coeffFilesToCheck = []
        allCoeffFiles = glob.glob("*.xml")

        if filenameString is None or not neededCoeffs:
            return

        for coeffFile in allCoeffFiles:
            if filenameString in coeffFile and 'test' not in coeffFile:  # Don't check test files
                coeffFilesToCheck.append(coeffFile)

        for coeffFile in coeffFilesToCheck:
            try:
                xmlCoeffObject = xmlParser.parse(coeffFile)
                coeffNames = []
                for coeff in xmlCoeffObject.iter('Coeff'):
                    coeffNames.append(coeff.get('id'))
                for coeff in neededCoeffs:
                    if coeff not in coeffNames:
                        raise Exception
            except Exception:
                self.log.error(coeffFile + " is missing a needed coeff " + coeff)
                self.incorrectFiles.append(coeffFile)
        assert len(self.incorrectFiles) == 0

    def checkValidSchema(self, schema, directory, filenameStringPatternToCheck):
        parser = self.getSchemaParser(schema)
        os.chdir(directory)

        if not filenameStringPatternToCheck is None:  # hacky way to skip some things.Giggity
            for coeffFile in glob.glob("*.xml"):
                if 'test' not in coeffFile and filenameStringPatternToCheck in coeffFile:
                    try:
                        root = xmlParser.parse(coeffFile, parser)
                        self.correctFiles.append(coeffFile)
                    except xmlParser.XMLSyntaxError:
                        self.log.error(coeffFile + " has coeffs that are not in the schema")
                        self.incorrectFiles.append(coeffFile)

        assert len(self.incorrectFiles) == 0

    ###################################################################################
    #   Check that actuator coeff files only have coeffs that should be in them.      #
    ###################################################################################
    def testActuatorCoeffsValidSchema(self):
        # Assemble the schema
        for classToCheck in classToActuatorCoeffFilenameDictionary:
            schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.safety_file_definitions + coeffSchemaDefinitions.sensor_files_definition + coeffSchemaDefinitions.mode_file_definitions + coeffSchemaDefinitions.location_files_definition + classToActuatorSchemaDictionary[classToCheck] + \
                coeffSchemaDefinitions.header_coeff_definition + classToActuatorCoeffFilesSchemaDictionary[classToCheck] + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
            self.checkValidSchema(schema, self.actuatorCoeffDirectory, classToActuatorCoeffFilenameDictionary[classToCheck])

    ###################################################################################
    #   Check that actuator coeff files have no duplicate coeffs.                     #
    ###################################################################################
    def testActuatorNoDuplicateCoeffs(self):
        self.checkForDuplicates(self.actuatorCoeffDirectory)

    ####################################################################################
    #    Check that actuator coeff files have coeffs that need to be in them.          #
    ####################################################################################
    def testActuatorEssentialCoeffs(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            self.checkForNeeded(self.actuatorCoeffDirectory, classLetter, coeffCollectionDefinitions.ActuatorNeededCoeffs[classLetter], classToActuatorCoeffFilenameDictionary[classLetter])

    ####################################################################################
    #    Check that class coeff files only have coeffs that should be in them.         #
    ####################################################################################
    def testClassCoeffsValidSchema(self):
        # Assemble the schema
        for classToCheck in classToActuatorCoeffFilenameDictionary:
            schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.class_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.actuator_class_info_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
            self.checkValidSchema(schema, self.classCoeffDirectory, coeffCollectionDefinitions.AllowedClassFiles[classToCheck])

    ####################################################################################
    #    Check that class coeff files have no duplicate coeffs.                        #
    ####################################################################################
    def testClassNoDuplicateCoeffs(self):
        self.checkForDuplicates(self.classCoeffDirectory)

    ####################################################################################
    #    Check that class coeff files have coeffs that need to be in them.             #
    ####################################################################################
    def testClassEssentialCoeffs(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            self.checkForNeeded(self.classCoeffDirectory, classLetter, coeffCollectionDefinitions.ClassNeededCoeffs[classLetter], coeffCollectionDefinitions.AllowedClassFiles[classLetter])

    ####################################################################################
    #    Check that controller coeff files only have coeffs that should be in them.    #
    ####################################################################################
    def testControllerCoeffsValidSchema(self):
        # Assemble the schema
        for classLetter in classToActuatorCoeffFilenameDictionary:
            schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.controller_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
            for controllerFile in coeffCollectionDefinitions.AllowedControllerFiles[classLetter]:
                self.checkValidSchema(schema, self.controllerCoeffDirectory, controllerFile)

    ####################################################################################
    #    Check that controller coeff files have no duplicate coeffs.                   #
    ####################################################################################
    def testControllerNoDuplicateCoeffs(self):
        self.checkForDuplicates(self.controllerCoeffDirectory)

    ####################################################################################
    #    Check that controller coeff files have coeffs that need to be in them.        #
    ####################################################################################
    def testControllerEssentialCoeffs(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            for filename in coeffCollectionDefinitions.AllowedControllerFiles[classLetter]:
                self.checkForNeeded(self.controllerCoeffDirectory, classLetter, coeffCollectionDefinitions.ControllerNeededCoeffs, filename)

    ####################################################################################
    #    Check that location coeff files only have coeffs that should be in them.      #
    ####################################################################################
    def testLocationCoeffsValidSchema(self):
        # Assemble the schema
        for classLetter in classToActuatorCoeffFilenameDictionary:
            schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.location_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
            for locationFile in coeffCollectionDefinitions.AllowedLocationFiles[classLetter]:
                self.checkValidSchema(schema, self.locationCoeffDirectory, locationFile)

    ####################################################################################
    #    Check that location coeff files have no duplicate coeffs.                     #
    ####################################################################################
    def testLocationNoDuplicateCoeffs(self):
        self.checkForDuplicates(self.locationCoeffDirectory)

    ####################################################################################
    #    Check that location coeff files have coeffs that need to be in them.          #
    ####################################################################################
    def testLocationEssentialCoeffs(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            for filename in coeffCollectionDefinitions.AllowedLocationFiles[classLetter]:
                self.checkForNeeded(self.locationCoeffDirectory, classLetter, coeffCollectionDefinitions.LocationNeededCoeffs[classLetter], filename)

    ####################################################################################
    #    Check that mode coeff files only have coeffs that should be in them.          #
    ####################################################################################
    def testModesCoeffsValidSchema(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.modes_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
            self.checkValidSchema(schema, self.modesCoeffDirectory, coeffCollectionDefinitions.AllowedModeFiles[classLetter])

    ####################################################################################
    #    Check that mode coeff files have no duplicate coeffs.                         #
    ####################################################################################
    def testModeNoDuplicateCoeffs(self):
        self.checkForDuplicates(self.modesCoeffDirectory)

    ####################################################################################
    #    Check that mode coeff files have coeffs that need to be in them.              #
    ####################################################################################
    def testModeEssentialCoeffs(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            self.checkForNeeded(self.modesCoeffDirectory, classLetter, coeffCollectionDefinitions.ModesNeededCoeffs, coeffCollectionDefinitions.AllowedModeFiles[classLetter])

    ####################################################################################
    #    Check that safety coeff files only have coeffs that should be in them.        #
    ####################################################################################
    def testSafetyCoeffsValidSchema(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.safety_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
            self.checkValidSchema(schema, self.safetyCoeffDirectory, coeffCollectionDefinitions.AllowedSafetyFiles[classLetter])

    ####################################################################################
    #    Check that safety coeff files have no duplicate coeffs.                       #
    ####################################################################################
    def testSafetyNoDuplicateCoeffs(self):
        self.checkForDuplicates(self.safetyCoeffDirectory)

    ####################################################################################
    #    Check that safety coeff files have coeffs that need to be in them.            #
    ####################################################################################
    def testSafetyEssentialCoeffs(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            self.checkForNeeded(self.safetyCoeffDirectory, classLetter, coeffCollectionDefinitions.SafetyNeededCoeffs, coeffCollectionDefinitions.AllowedSafetyFiles[classLetter])

    ####################################################################################
    #    Check that sensor coeff files only have coeffs that should be in them.        #
    ####################################################################################
    def testSensorCoeffsValidSchema(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            schema = coeffSchemaDefinitions.schema_header + coeffSchemaDefinitions.sensor_coeffs_definition + coeffSchemaDefinitions.header_coeff_definition + coeffSchemaDefinitions.coeff_definition + coeffSchemaDefinitions.footer_coeff_definition
            self.checkValidSchema(schema, self.sensorCoeffDirectory, coeffCollectionDefinitions.AllowedSensorFiles[classLetter])

    ####################################################################################
    #    Check that sensor coeff files have no duplicate coeffs.                       #
    ####################################################################################
    def testSensorNoDuplicateCoeffs(self):
        self.checkForDuplicates(self.sensorCoeffDirectory)

    ####################################################################################
    #    Check that sensor coeff files have coeffs that need to be in them.            #
    ####################################################################################
    def testSensorEssentialCoeffs(self):
        for classLetter in classToActuatorCoeffFilenameDictionary:
            self.checkForNeeded(self.sensorCoeffDirectory, classLetter, coeffCollectionDefinitions.SensorNeededCoeffs, coeffCollectionDefinitions.AllowedSensorFiles[classLetter])
